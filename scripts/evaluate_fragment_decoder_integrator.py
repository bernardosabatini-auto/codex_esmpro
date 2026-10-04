"""Frozen native-context integration and oracle-path diagnostic."""
import argparse,json,time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.decoder import load_proteinae
from latentfold.fragment_decoder_fm import FragmentDenoisingDecoder,denoising_inputs
from latentfold.fragment_decoder_integrator import decode_steps
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from fragment_decoder_integrator_core import audit
from native_anchor_training_core import state_hash
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec,gc,source=audit(c)
    a.output.mkdir(exist_ok=False);tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,training_updates_executed=0,controls=[],timing=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        codec=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval()
        model=FragmentDenoisingDecoder(codec,seed=gc['spec']['seed']).cuda().eval()
        saved=torch.load(c['checkpoint'],map_location='cpu',weights_only=True)
        if saved['config']!=gc:raise ValueError('Changed trained model config')
        model.load_state_dict(saved['ema']);del saved
        model.requires_grad_(False);codec.requires_grad_(False)
        m['model_initial']=state_hash(model.state_dict());m['original_initial']=state_hash(codec.decoder.state_dict())
        if m['model_initial']!=source['evaluated_model_sha256'] or m['original_initial']!=source['frozen_original']:raise ValueError('Changed original or trained weights')
        items=load_conditions(c['fragments'],[r['id'] for r in c['selected']],'c20_center',cohort='train')
        pose_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
        telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as fr,h5py.File(c['source_predictions']) as prior,h5py.File(a.output/'predictions.h5','x') as out:
            for row in c['selected']:
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Integration diagnostic work cap')
                ident=row['id'];item=items[ident];n=row['length'];b=spec['samples']
                context=torch.from_numpy(fr['train/'+ident+'/reference_z'][:])[None].expand(b,-1,-1).cuda()
                target=torch.from_numpy(fr['train/'+ident+'/reference_backbone'][:])[None].expand(b,-1,-1,-1).cuda()
                mask=torch.ones(b,n,dtype=torch.bool,device='cuda');keep=item['keep'][None].expand(b,-1).cuda()
                features=item['features'][None].expand(b,-1,-1).cuda();coords=item['coordinates'][None].expand(b,-1,-1).cuda()
                noise=torch.cat([target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=k,stream=spec['decoder_stream'],device='cuda') for k in range(b)])*model.scale_ref
                inputs=out.create_group('inputs/'+ident);inputs['noise']=noise.cpu().numpy();inputs['masked_latent']=torch.where(keep[...,None],torch.zeros_like(context),context).cpu().numpy()
                original=codec(context,mask,noise=noise,return_backbone=True)[1];error=float(np.max(abs(original.cpu().numpy()-prior['native_direct/'+ident+'/backbone'][:])))
                if error>1e-5:raise ValueError('Original native decode parity failed')
                out.create_dataset('original_native/'+ident+'/backbone',data=original.cpu().numpy());m['controls'].append(dict(kind='original_native',target_id=ident,max_abs=error))
                for dropped in (False,True):
                    arm='null' if dropped else 'cond'
                    for steps in spec['steps']:
                        torch.cuda.synchronize();start=time.monotonic()
                        bb=decode_steps(model,context,features,keep,mask,coords,noise=noise,steps=steps,drop_fragment=dropped)
                        torch.cuda.synchronize();m['timing'].append(dict(target_id=ident,arm=arm,steps=steps,seconds=time.monotonic()-start))
                        g=out.create_group(f'free/{arm}/{steps}/{ident}');g['backbone']=bb.cpu().numpy()
                        if steps==3:
                            error=float(np.max(abs(bb.cpu().numpy()-prior['native_'+arm+'/'+ident+'/backbone'][:])))
                            if error>1e-5:raise ValueError('Three-step archived output changed')
                            m['controls'].append(dict(kind='three_'+arm,target_id=ident,max_abs=error))
                        if steps==10 and not dropped and ident in pose_ids:
                            posed=(coords.double()@coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11)*keep[...,None]
                            pb=decode_steps(model,context,features,keep,mask,posed,noise=noise,steps=10)
                            error=float((bb-pb).abs().max())
                            if error>1e-4:raise ValueError('Ten-step fragment pose control failed')
                            g['pose_backbone']=pb.cpu().numpy();m['controls'].append(dict(kind='pose_ten_cond',target_id=ident,max_abs=error))
                for index,value in enumerate(spec['probe_times']):
                    t=noise.new_full((b,),value);clean,_,noisy=denoising_inputs(target,noise,t)
                    for arm in ('cond','null','original_unmasked'):
                        if arm=='original_unmasked':
                            velocity=codec.decoder(dict(x_t=noisy,t=t,mask=mask,coords_mask=mask.repeat_interleave(4,1),single_repr=context))['coors_pred']
                        else:
                            dropped=torch.full((b,),arm=='null',dtype=torch.bool,device='cuda')
                            velocity=model.velocity(context,features,keep,mask,coords,noisy,t,dropped,checkpointed=False)
                        predicted=noisy+(1-t[:,None,None])*velocity
                        g=out.create_group(f'path/{arm}/{index}/{ident}');g.attrs['t']=float(t[0]);g['velocity']=velocity.cpu().numpy();g['backbone']=(predicted.reshape(b,n,4,3)*10).cpu().numpy()
                out.flush();atomic_json(a.output/'manifest.json',m);print('diagnosed',ident,flush=True)
        m['model_final']=state_hash(model.state_dict());m['original_final']=state_hash(codec.decoder.state_dict());m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['model_final']!=m['model_initial'] or m['original_final']!=m['original_initial'] or m['peak_reserved_GiB']>75:raise ValueError('Changed frozen weights or exceeded memory bound')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
