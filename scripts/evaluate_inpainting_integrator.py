"""Frozen conditional-coordinate integration and native known-path diagnostic."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.fragment_inpainting import FragmentInpaintingDecoder,place_fragment,denoising_state,constrain_state,tangent_velocity
from latentfold.inpainting_integrator import decode_steps
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from inpainting_integrator_core import audit
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
        model=FragmentInpaintingDecoder(codec,seed=gc['spec']['seed']).cuda().eval()
        saved=torch.load(c['checkpoint'],map_location='cpu',weights_only=True)
        if saved['config']!=gc:raise ValueError('Changed source checkpoint config')
        model.load_state_dict(saved['ema']);del saved;model.requires_grad_(False)
        m['model_initial']=state_hash(model.state_dict());m['original_initial']=state_hash(codec.decoder.state_dict())
        if m['model_initial']!=source['evaluated_model_sha256'] or m['original_initial']!=source['frozen_original']:raise ValueError('Changed frozen weights')
        items=load_conditions(c['fragments'],[r['id'] for r in c['selected']],'c20_center',cohort='train')
        pose_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
        telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as fr,h5py.File(c['source_predictions']) as prior,h5py.File(a.output/'predictions.h5','x') as out:
            for row in c['selected']:
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Diagnostic work cap')
                ident=row['id'];item=items[ident];n=row['length'];b=4
                mask=torch.ones(b,n,dtype=torch.bool,device='cuda');keep=item['keep'][None].expand(b,-1).cuda()
                features=item['features'][None].expand(b,-1,-1).cuda();coords=item['coordinates'][None].expand(b,-1,-1).cuda()
                noise=torch.cat([target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=k,stream=spec['decoder_stream'],device='cuda') for k in range(b)])*model.scale_ref
                out.create_dataset('noise/'+ident,data=noise.cpu().numpy())
                for kind,group in [('generated','parent'),('native','native_direct')]:
                    context=torch.from_numpy(prior[group+'/'+ident+'/latent'][:]).cuda()
                    reference=torch.from_numpy(prior[group+'/'+ident+'/backbone'][:]).cuda()
                    anchors=place_fragment(torch.from_numpy(item['fragment']).cuda(),reference,item['start'])
                    out.create_dataset('anchors/'+kind+'/'+ident,data=anchors.cpu().numpy())
                    if kind=='native':
                        original=codec(context,mask,noise=noise,return_backbone=True)[1]
                        error=float((original-reference).abs().max())
                        if error>1e-5:raise ValueError('Original native replay changed')
                        out.create_dataset('original_native/'+ident,data=original.cpu().numpy());m['controls'].append(dict(kind='original_native',target_id=ident,max_abs=error))
                    for steps in spec['steps']:
                        torch.cuda.synchronize();start=time.monotonic()
                        bb=decode_steps(model,context,features,keep,mask,coords,anchors=anchors,noise=noise,steps=steps)
                        torch.cuda.synchronize();m['timing'].append(dict(target_id=ident,kind=kind,steps=steps,seconds=time.monotonic()-start))
                        g=out.create_group(f'free/{kind}/{steps}/{ident}');g['backbone']=bb.cpu().numpy()
                        if steps==3:
                            error=float(np.max(abs(bb.cpu().numpy()-prior[kind+'_cond/'+ident+'/backbone'][:])))
                            if error>1e-5:raise ValueError('Archived three-step output changed')
                            m['controls'].append(dict(kind='three_'+kind,target_id=ident,max_abs=error))
                        elif ident in pose_ids:
                            rot=coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)
                            fragment=torch.from_numpy(item['fragment']).cuda().double()@rot+11
                            posed=place_fragment(fragment,reference,item['start']);pc=(coords.double()@rot+11)*keep[...,None]
                            replay=decode_steps(model,context,features,keep,mask,pc,anchors=posed,noise=noise,steps=steps)
                            error=float((bb-replay).abs().max())
                            if error>1e-4:raise ValueError('Ten-step pose control failed')
                            g['pose_backbone']=replay.cpu().numpy();m['controls'].append(dict(kind='pose_'+kind,target_id=ident,max_abs=error))
                # These native path states expose the supervised endpoint through
                # the interpolation and are explicitly oracle, never generation.
                target=torch.from_numpy(fr['train/'+ident+'/reference_backbone'][:])[None].expand(b,-1,-1,-1).cuda()
                dropped=torch.zeros(b,dtype=torch.bool,device='cuda')
                for index,value in enumerate(spec['probe_times']):
                    t=noise.new_full((b,),value);clean,noisy,anchors,known=denoising_state(target,noise,t,keep,dropped)
                    for kind in ('trained','original_unmasked'):
                        if kind=='trained':v=model.velocity(context,features,keep,mask,coords,noisy,t,dropped,checkpointed=False)
                        else:v=codec.decoder(dict(x_t=noisy,t=t,mask=mask,coords_mask=mask.repeat_interleave(4,1),single_repr=context))['coors_pred']
                        predicted=constrain_state(noisy+(1-t[:,None,None])*tangent_velocity(v,known),anchors,known)
                        out.create_dataset(f'path/{kind}/{index}/{ident}',data=(predicted.reshape(b,n,4,3)*10).cpu().numpy())
                out.flush();atomic_json(a.output/'manifest.json',m);print('diagnosed',ident,flush=True)
        m['model_final']=state_hash(model.state_dict());m['original_final']=state_hash(codec.decoder.state_dict());m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['model_final']!=m['model_initial'] or m['original_final']!=m['original_initial'] or m['peak_reserved_GiB']>75:raise ValueError('Changed weights or memory bound')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
