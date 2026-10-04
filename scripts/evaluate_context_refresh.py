"""Frozen three-round context refresh; all scaffold coordinates can respond."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.fragment_inpainting import FragmentInpaintingDecoder,place_fragment
from latentfold.precision import inference_precision
from compatible_fragment_core import encoder
from context_refresh_core import audit,starting_state,refresh_rounds
from extra_fragment_validation_core import load_conditions
from native_anchor_training_core import state_hash
from profile_gpu import Telemetry,atomic_json
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec,gc,parent=audit(c,full=False);b=c['frame_config']['base']
    a.output.mkdir(exist_ok=False);tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],timing=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        codec=load_proteinae(a.source/'ProteinAE_v1',Path(b['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        models={mode:FragmentInpaintingDecoder(codec,seed=gc['spec']['seed']).cuda().eval().requires_grad_(False) for mode in ('trained','untrained')}
        saved=torch.load(b['checkpoint'],map_location='cpu',weights_only=True)
        if saved['config']!=gc:raise ValueError('Changed checkpoint config')
        models['trained'].load_state_dict(saved['ema']);del saved
        def hashes():return dict(trained=state_hash(models['trained'].state_dict()),untrained=state_hash(models['untrained'].state_dict()),
                                encoder=state_hash(codec.ae_model.encoder.state_dict()),decoder=state_hash(codec.decoder.state_dict()))
        m['initial_weights']=hashes();frame=json.loads(Path(c['frame_manifest']).read_text())
        if (m['initial_weights']['trained']!=parent['evaluated_model_sha256'] or m['initial_weights']['untrained']!=parent['initial_model_sha256']
                or any(m['initial_weights'][k]!=frame['initial_weights'][k] for k in ('encoder','decoder'))):raise ValueError('Changed frozen models')
        ids=[r['id'] for r in c['selected']];control_ids={r['id'] for r in c['frame_config']['selected']}
        items=load_conditions(b['fragments'],ids,'c20_center',cohort='train');telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(b['source_predictions']) as prior, \
             h5py.File(c['starting_backbones']) as starts,h5py.File(b['noise_source']) as noises,h5py.File(a.output/'predictions.h5','x') as out:
            for row in c['selected']:
                ident=row['id'];item=items[ident];n=row['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda')
                features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda()
                noise=torch.from_numpy(noises['noise/'+ident][:]).cuda();out['noise/'+ident]=noise.cpu().numpy()
                for mode,model in models.items():
                    start_arm='generated_cond' if mode=='trained' else 'generated_untrained'
                    current,anchors=starting_state(torch.from_numpy(starts[start_arm+'/'+ident+'/backbone'][:]).cuda(),keep)
                    g=out.create_group(mode+'/'+ident)
                    for key,value in dict(start=current,anchors=anchors,features=features,keep=keep,coordinates=coords).items():g[key]=value.cpu().numpy()
                    def decode(z,eps=noise,coordinate=coords):return model(z,features,keep,mask,coordinate,anchors=anchors,noise=eps)
                    def control(name,result,expected,threshold):
                        error=float((result-expected).abs().max());g['controls/'+name]=result.cpu().numpy()
                        m['controls'].append(dict(kind=name,arm=mode,target_id=ident,max_abs=error))
                        if error>threshold:raise ValueError('Failed refresh control: '+name)
                    if ident in control_ids:
                        original=torch.from_numpy(prior['parent/'+ident+'/latent'][:]).cuda()
                        reference=torch.from_numpy(prior['parent/'+ident+'/backbone'][:]).cuda()
                        replay=model(original,features,keep,mask,coords,anchors=place_fragment(torch.from_numpy(item['fragment']).cuda(),reference,item['start']),noise=noise)
                        control('desired_replay',replay,torch.from_numpy(prior[start_arm+'/'+ident+'/backbone'][:]).cuda(),1e-5)
                    torch.cuda.synchronize();started=time.monotonic()
                    for index,previous,latent,bb in refresh_rounds(current,lambda x:encoder(codec,x),decode):
                        if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Refresh work cap')
                        q=g.create_group('round'+str(index));q['input']=previous.cpu().numpy();q['latent']=latent.cpu().numpy();q['backbone']=bb.cpu().numpy()
                        if float((bb[keep]-anchors[keep]).abs().max())>1e-4 or float(bb.mean((1,2)).abs().max())>1e-4:raise ValueError('Fixed anchor or centered frame drift')
                        if index==1 and ident in control_ids:
                            control('repeat',decode(latent),bb,1e-5)
                            hidden=latent.clone();hidden[keep]+=97;eps=noise.clone();eps[keep.repeat_interleave(4,1)]+=111
                            control('nonleak',decode(hidden,eps=eps),bb,1e-5)
                            rotation=coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)
                            posed=(coords.double()@rotation+11)*keep[...,None]
                            control('pose',decode(latent,coordinate=posed),bb,1e-4)
                    torch.cuda.synchronize();m['timing'].append(dict(arm=mode,target_id=ident,seconds=time.monotonic()-started))
                out.flush();atomic_json(a.output/'manifest.json',m);print('refresh',ident,flush=True)
        m['final_weights']=hashes();m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['initial_weights']!=m['final_weights'] or m['peak_reserved_GiB']>75:raise ValueError('Changed weights or exceeded memory')
        audit(c,full=False);m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
