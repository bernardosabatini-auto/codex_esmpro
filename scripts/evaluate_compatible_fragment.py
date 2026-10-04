"""Frozen desired-versus-self-compatible fragment diagnostic, never a success assay."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.fragment_inpainting import FragmentInpaintingDecoder,place_fragment
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from compatible_fragment_core import audit,assemble_inputs,encoder
from extra_fragment_validation_core import load_conditions
from native_anchor_training_core import state_hash
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec,gc,parent=audit(c)
    a.output.mkdir(exist_ok=False);tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],timing=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        codec=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        models={mode:FragmentInpaintingDecoder(codec,seed=gc['spec']['seed']).cuda().eval().requires_grad_(False) for mode in ('trained','untrained')}
        saved=torch.load(c['checkpoint'],map_location='cpu',weights_only=True)
        if saved['config']!=gc:raise ValueError('Changed checkpoint config')
        models['trained'].load_state_dict(saved['ema']);del saved
        def hashes():return dict(trained=state_hash(models['trained'].state_dict()),untrained=state_hash(models['untrained'].state_dict()),
                                decoder=state_hash(codec.decoder.state_dict()),encoder=state_hash(codec.ae_model.encoder.state_dict()))
        m['initial_weights']=hashes()
        if (m['initial_weights']['trained']!=parent['evaluated_model_sha256'] or m['initial_weights']['untrained']!=parent['initial_model_sha256']
                or m['initial_weights']['decoder']!=parent['frozen_original']):raise ValueError('Changed frozen initialization')
        telemetry=Telemetry(a.output,True)
        ids=[r['id'] for r in c['selected']];items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
        control_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['source_predictions']) as prior, \
             h5py.File(c['noise_source']) as archived_noise,h5py.File(c['fragments']) as fr,h5py.File(a.output/'predictions.h5','x') as out:
            for row in c['selected']:
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Compatibility diagnostic work cap')
                ident=row['id'];item=items[ident];n=row['length'];start=item['start']
                sequence=str(fr['train/'+ident+'/conditions/c20_center'].attrs['sequence'])
                mask=torch.ones(4,n,dtype=torch.bool,device='cuda')
                noise=torch.cat([target_noise([ident],[4*n],3,seed=gc['spec']['sampling_seed'],sample_index=k,
                    stream='decoder:0',device='cuda') for k in range(4)])*models['trained'].scale_ref
                if not np.array_equal(noise.cpu().numpy(),archived_noise['noise/'+ident][:]):raise ValueError('Archived decoder noises changed')
                out.create_dataset('noise/'+ident,data=noise.cpu().numpy())
                encoded=encoder(codec,torch.from_numpy(item['fragment'])[None].cuda())[0]
                expected=item['features'][item['keep'],:8].cuda();error=float((encoded-expected).abs().max())
                out.create_dataset('controls/encoding/'+ident,data=encoded.cpu().numpy())
                m['controls'].append(dict(kind='encoding',target_id=ident,max_abs=error))
                if error>1e-4:raise ValueError('Stored isolated encoder convention changed')
                for kind,group in (('generated','parent'),('native','native_direct')):
                    reference=torch.from_numpy(prior[group+'/'+ident+'/backbone'][:]).cuda()
                    context=torch.from_numpy(prior[group+'/'+ident+'/latent'][:]).cuda()
                    inputs=assemble_inputs(reference,sequence,start,lambda x:encoder(codec,x))
                    g=out.create_group('inputs/'+kind+'/'+ident)
                    for key,value in inputs.items():g[key]=value.cpu().numpy()
                    g['context']=context.cpu().numpy();g.attrs['sequence']=sequence;g.attrs['start']=start
                    def decode(model,values=inputs,z=context,eps=noise):
                        return model(z,values['features'],values['keep'],mask,values['coordinates'],anchors=values['anchors'],noise=eps)
                    for mode,model in models.items():
                        arm=mode+'_'+kind+'_compatible';torch.cuda.synchronize();started=time.monotonic()
                        bb=decode(model);torch.cuda.synchronize();out.create_dataset(arm+'/'+ident+'/backbone',data=bb.cpu().numpy())
                        m['timing'].append(dict(arm=arm,target_id=ident,seconds=time.monotonic()-started))
                        if ident in control_ids:
                            hidden=context.clone();hidden[inputs['keep']]+=97
                            eps=noise.clone();eps[inputs['keep'].repeat_interleave(4,1)]+=111
                            repeat=decode(model,z=hidden,eps=eps);error=float((repeat-bb).abs().max())
                            out.create_dataset('controls/nonleak/'+arm+'/'+ident,data=repeat.cpu().numpy())
                            m['controls'].append(dict(kind='nonleak',arm=arm,target_id=ident,max_abs=error))
                            if error>1e-5:raise ValueError('Hidden motif codes or known-atom noise leaked')
                    if ident in control_ids:
                        original=codec(context,mask,noise=noise,return_backbone=True)[1]
                        error=float((original-reference).abs().max());out.create_dataset('controls/original/'+kind+'/'+ident,data=original.cpu().numpy())
                        m['controls'].append(dict(kind='original_'+kind,target_id=ident,max_abs=error))
                        if error>1e-5:raise ValueError('Original parent replay changed')
                        feat=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda()
                        anchor=place_fragment(torch.from_numpy(item['fragment']).cuda(),reference,start)
                        desired=models['trained'](context,feat,keep,mask,coords,anchors=anchor,noise=noise)
                        error=float(np.max(np.abs(desired.cpu().numpy()-prior[kind+'_cond/'+ident+'/backbone'][:])))
                        out.create_dataset('controls/desired/'+kind+'/'+ident,data=desired.cpu().numpy());m['controls'].append(dict(kind='desired_'+kind,target_id=ident,max_abs=error))
                        if error>1e-5:raise ValueError('Desired-fragment historical replay changed')
                        posed=assemble_inputs(reference,sequence,start,lambda x:encoder(codec,x),posed=True)
                        error=float((posed['isolated_latent']-inputs['isolated_latent']).abs().max())
                        out.create_dataset('controls/pose_latent/'+kind+'/'+ident,data=posed['isolated_latent'].cpu().numpy())
                        m['controls'].append(dict(kind='pose_encoding_'+kind,target_id=ident,max_abs=error))
                        if error>1e-4:raise ValueError('Isolated fragment encoder pose control failed')
                        replay=decode(models['trained'],values=posed)
                        expected=out['trained_'+kind+'_compatible/'+ident+'/backbone'][:]
                        error=float(np.max(np.abs(replay.cpu().numpy()-expected)))
                        out.create_dataset('controls/pose/'+kind+'/'+ident,data=replay.cpu().numpy());m['controls'].append(dict(kind='pose_'+kind,target_id=ident,max_abs=error))
                        if error>1e-4:raise ValueError('Compatible fragment pose control failed')
                out.flush();atomic_json(a.output/'manifest.json',m);print('compatible',ident,flush=True)
        m['final_weights']=hashes();m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['final_weights']!=m['initial_weights'] or m['peak_reserved_GiB']>75:raise ValueError('Weights changed or memory exceeded')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
