"""Profile/train a local conditional flow; preserve every generated sample."""
import argparse,math,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.masked_fragment_flow import MaskedFragmentFlow,masked_flow_loss,sample_masked_fragment,editable_window
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from evaluate_decoder_fragment_variance import check_backbones
from masked_fragment_training_core import audit,load_training,training_batch,panel
from native_anchor_training_core import state_hash,tensor_hash
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit(c);data=load_training(c);selected=panel(c)
    items=load_conditions(c['fragments'],[r['id'] for r in selected],'c20_center',cohort='train')
    a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,training=[],controls=[],evaluations=[],updates=0);telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);torch.manual_seed(spec['seed'])
        model=MaskedFragmentFlow(**spec['architecture']).cuda();m['initial_model_sha256']=state_hash(model.state_dict());m['trainable_parameters']=sum(p.numel() for p in model.parameters())
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);m['initial_codec_sha256']=state_hash(decoder.state_dict())
        ema={k:v.detach().clone() for k,v in model.state_dict().items()};optimizer=torch.optim.AdamW(model.parameters(),lr=spec['learning_rate'],betas=(.9,.95),weight_decay=.01,foreach=False)
        order=np.random.default_rng(spec['seed']);rng=torch.Generator(device='cuda').manual_seed(spec['seed']);telemetry=Telemetry(a.output,True)
        buckets={b:sorted(i for i,r in data.items() if r['bucket']==b) for b in (128,256,384,512)}
        if not all(buckets.values()):raise ValueError('Missing training length stratum')
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();start=time.monotonic();model.train()
        with inference_precision('fp32'):
            for step in range(c['updates']):
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Masked training work cap')
                length=(128,256,384,512)[step%4];batch=spec['batches'][str(length)];ids=order.choice(buckets[length],size=batch).tolist();names=order.choice(spec['conditions'],size=batch).tolist()
                z,features,keep,mask,coords=[x.cuda() for x in training_batch(data,ids,names,length)]
                factor=min((step+1)/spec['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
                for group in optimizer.param_groups:group['lr']=spec['learning_rate']*factor
                optimizer.zero_grad(set_to_none=True);loss,info=masked_flow_loss(model,z,features,keep,mask,coords,generator=rng,flank=spec['flank']);loss.backward()
                norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
                if not torch.isfinite(loss) or not torch.isfinite(norm) or norm<=0:raise FloatingPointError('Nonfinite or zero repair gradient')
                optimizer.step()
                with torch.no_grad():
                    for key,value in model.state_dict().items():
                        if value.is_floating_point():ema[key].lerp_(value,1-spec['ema_decay'])
                m['updates']=step+1;m['training'].append(dict(step=step+1,length=length,batch=batch,ids=ids,conditions=names,loss=float(loss.detach()),gradient_norm=float(norm),learning_rate_factor=factor,
                    target_sha256=tensor_hash(z),noise_sha256=tensor_hash(info['noise']),time_sha256=tensor_hash(info['t']),drop_sha256=tensor_hash(info['dropped'])))
                if step+1==spec['profile_updates'] and not c['profile_only']:
                    torch.save(dict(raw={k:v.detach().cpu() for k,v in model.state_dict().items()},ema={k:v.cpu() for k,v in ema.items()}),a.output/'prefix_40.pt');m['prefix_sha256']=sha(a.output/'prefix_40.pt')
                if (step+1)%(10 if c['profile_only'] else 100)==0:atomic_json(a.output/'manifest.json',m)
                if (step+1)%50==0 or c['profile_only'] and (step+1)%10==0:print('update',step+1,'loss',float(loss.detach()),flush=True)
                del loss,info,z,features,keep,mask,coords
        torch.cuda.synchronize();m['training_seconds']=time.monotonic()-start;m['training_peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30;m['final_model_sha256']=state_hash(model.state_dict())
        if m['initial_model_sha256']==m['final_model_sha256']:raise ValueError('Repair model did not update')
        torch.save(dict(raw={k:v.detach().cpu() for k,v in model.state_dict().items()},ema={k:v.cpu() for k,v in ema.items()},config=c),a.output/'checkpoint.pt');m['checkpoint_sha256']=sha(a.output/'checkpoint.pt');model.load_state_dict(ema);model.eval()
        if not c['profile_only']:
            old=json.loads(Path(c['profile_manifest']).read_text());keys=('step','length','batch','ids','conditions','learning_rate_factor','target_sha256','noise_sha256','time_sha256','drop_sha256')
            if old['initial_model_sha256']!=m['initial_model_sha256'] or any(x[k]!=y[k] for x,y in zip(old['training'],m['training'][:40]) for k in keys):raise ValueError('Profile/full training draws differ')
        start=time.monotonic()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['baseline_predictions']) as parent,h5py.File(c['diagnostic_predictions']) as diagnostic,h5py.File(c['fragments']) as fr,h5py.File(a.output/'predictions.h5','x') as out:
            for source in selected:
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Repair evaluation work cap')
                ident=source['id'];item=items[ident];n=item['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda()
                generated=torch.from_numpy(parent['new/'+ident+'/latent'][:]).cuda();native=torch.from_numpy(fr['train/'+ident+'/reference_z'][:]).cuda()[None].expand(4,-1,-1)
                noise=torch.cat([target_noise([ident],[n],8,seed=spec['sampling_seed'],sample_index=k,stream=spec['sampling_stream'],device='cuda') for k in range(4)])
                dn=torch.cat([target_noise([ident],[4*n],3,seed=spec['sampling_seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                for kind,context,reference in [('parent',generated,parent['new/'+ident+'/backbone'][:]),('native_direct',native,diagnostic['native/'+ident+'/backbone'][:4])]:
                    _,bb=decoder(context,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();g=out.create_group(kind+'/'+ident);g['latent']=context.cpu().numpy();g['backbone']=bb
                    m['controls'].append(dict(kind=kind,target_id=ident,**check_backbones(bb,reference,item['fragment'],item['start'],ident)))
                for kind,context in [('generated',generated),('native',native)]:
                    for dropped in (False,True):
                        arm=kind+('_null' if dropped else '_cond');torch.cuda.synchronize();sample_start=time.monotonic()
                        z=sample_masked_fragment(model,context,features,keep,mask,coords,noise=noise,steps=spec['steps'],flank=spec['flank'],drop_fragment=dropped)
                        _,bb=decoder(z,mask,noise=dn,return_backbone=True);torch.cuda.synchronize();g=out.create_group(arm+'/'+ident);g['latent']=z.cpu().numpy();g['backbone']=bb.cpu().numpy()
                        m['evaluations'].append(dict(arm=arm,target_id=ident,seconds=time.monotonic()-sample_start))
                        if not dropped:
                            posed=(coords.double()@coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11)*keep[...,None]
                            pz=sample_masked_fragment(model,context,features,keep,mask,posed,noise=noise,steps=spec['steps'],flank=spec['flank']);error=float((z-pz).abs().max());g['pose_latent']=pz.cpu().numpy()
                            if error>1e-4:raise ValueError('Repair fragment-coordinate pose control failed')
                            m['controls'].append(dict(kind=arm+'_pose',target_id=ident,latent_max_abs=error))
                out.flush();atomic_json(a.output/'manifest.json',m);print('evaluated',ident,flush=True)
        m['evaluation_seconds']=time.monotonic()-start;m['final_codec_sha256']=state_hash(decoder.state_dict());m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['initial_codec_sha256']!=m['final_codec_sha256'] or m['peak_reserved_GiB']>75:raise ValueError('Changed codec or failed memory profile')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
