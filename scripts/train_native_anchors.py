"""Matched positive-only/contrastive adaptation with a frozen learned generator."""
import argparse
import copy
import json
import math
import time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.anchored_preference import native_preference_flow_loss
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_cross_attention import load_fragment_adapter
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from fragment_validation_core import raw_rows
from native_anchor_training_core import audit,load_pairs,state_hash,tensor_hash
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec,labels=audit(c);data=load_pairs(c)
    controls=load_conditions(c['fragments'],c['control_ids'],'c20_center',cohort='train')
    a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,updates=0,training=[],controls=[],evaluations=[]);telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        net,arch=load_legacy(c['checkpoint'],trusted_pickle=True);net.cuda().requires_grad_(False);net.checkpoint_blocks=True
        ck=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True)
        adapter=load_fragment_adapter(ck,net).cuda();adapter_config=ck['adapter_config'];del ck
        reference=copy.deepcopy(adapter).eval().requires_grad_(False)
        if any(isinstance(module,torch.nn.Dropout) and module.p for module in net.modules()):raise ValueError('Unexpected stochastic frozen backbone')
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        m.update(generator_initial=state_hash(net.state_dict()),adapter_initial=state_hash(adapter.state_dict()),reference_initial=state_hash(reference.state_dict()),trainable_parameters=sum(p.numel() for p in adapter.parameters()))
        ema={k:v.detach().clone() for k,v in adapter.state_dict().items()}
        optimizer=torch.optim.AdamW(adapter.parameters(),lr=spec['adapter_lr'],betas=tuple(spec['optimizer']['betas']),weight_decay=spec['optimizer']['weight_decay'],foreach=False)
        torch.manual_seed(spec['seed']);order=np.random.default_rng(spec['seed']);rng=torch.Generator(device='cuda').manual_seed(spec['seed']);telemetry=Telemetry(a.output,True)
        buckets={b:sorted(i for i,r in data.items() if r['bucket']==b) for b in (128,256,384,512)};active=[b for b in buckets if buckets[b]];m['active_buckets']=active
        def evaluate(step):
            saved_rng=torch.cuda.get_rng_state();raw={k:v.detach().clone() for k,v in adapter.state_dict().items()};adapter.load_state_dict(ema);adapter.eval();net.eval();start=time.monotonic();rows=[]
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/f'evaluation_{step}.h5','x') as out,h5py.File(c['initial_predictions']) as historical:
                for ident,item in controls.items():
                    n=item['length'];features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda();mask=torch.ones(4,n,dtype=torch.bool,device='cuda')
                    noise=torch.cat([target_noise([ident],[n],8,seed=c['sampling_seed'],sample_index=k,stream='flow:0',device='cuda') for k in range(4)])
                    dn=torch.cat([target_noise([ident],[4*n],3,seed=c['sampling_seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                    for mode in ('conditioned','null'):
                        z=sample_fragment(net,adapter,features,keep,mask,noise=noise,coordinates=coords,drop_fragment=mode=='null');_,bb=decoder(z,mask,noise=dn,return_backbone=True);z=z.cpu().numpy();bb=bb.cpu().numpy()
                        g=out.create_group(mode+'/'+ident);g['latent']=z;g['backbone']=bb
                        if step==0 and mode=='conditioned':
                            hz=historical['new/'+ident+'/latent'][:];hb=historical['new/'+ident+'/backbone'][:]
                            metrics=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,hb)]
                            control=dict(kind='initial',step=step,target_id=ident,latent_max_abs=float(np.max(abs(z-hz))),max_ca_rmsd=max(r['ca_rmsd'] for r in metrics),min_ca_lddt=min(r['ca_lddt'] for r in metrics))
                            left=raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family']);right=raw_rows(hb,item['fragment'],item['start'],c['arm'],ident,item['family'])
                            control['same_decisions']=all(x[k]==y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed'));m['controls'].append(control)
                            if control['latent_max_abs']>1e-5 or control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99 or not control['same_decisions']:raise ValueError('Parent initialization changed')
                        if step and mode=='null':
                            with h5py.File(a.output/'evaluation_0.h5') as initial:hz=initial['null/'+ident+'/latent'][:];hb=initial['null/'+ident+'/backbone'][:]
                            metrics=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,hb)];control=dict(kind='null',step=step,target_id=ident,latent_max_abs=float(np.max(abs(z-hz))),max_ca_rmsd=max(r['ca_rmsd'] for r in metrics),min_ca_lddt=min(r['ca_lddt'] for r in metrics));m['controls'].append(control)
                            if control['latent_max_abs']>1e-5 or control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99:raise ValueError('Frozen null branch changed')
                        if mode=='conditioned':
                            posed=(coords.double()@coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11)*keep[...,None]
                            check=sample_fragment(net,adapter,features,keep,mask,noise=noise,coordinates=posed).cpu().numpy();g['pose_latent']=check;error=float(np.max(abs(z-check)));m['controls'].append(dict(kind='pose',step=step,target_id=ident,latent_max_abs=error))
                            if error>1e-4:raise ValueError('Fragment pose invariance failed')
                            rows.extend(raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family']))
                    out.flush();atomic_json(a.output/'manifest.json',m)
            m['evaluations'].append(dict(step=step,seconds=time.monotonic()-start,records=rows));adapter.load_state_dict(raw);net.train();adapter.train();torch.cuda.set_rng_state(saved_rng)
        evaluate(0)
        torch.cuda.reset_peak_memory_stats();start=time.monotonic()
        with inference_precision('fp32'):
            for step in range(c['updates']):
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Native training cap')
                length=active[step%len(active)];batch=spec['batches'][str(length)];ids=order.choice(buckets[length],size=batch).tolist()
                positive=torch.zeros(batch,length,8);negative=None if c.get('positive_coverage_training') else torch.zeros_like(positive);features=torch.zeros(batch,length,29);keep=torch.zeros(batch,length,dtype=torch.bool);mask=torch.zeros_like(keep);coords=torch.zeros(batch,length,3)
                for k,ident in enumerate(ids):
                    v=data[ident];n=v['length'];positive[k,:n]=v['positive'];features[k,:n]=v['features'];keep[k,:n]=v['keep'];coords[k,:n]=v['coordinates'];mask[k,:n]=True
                    if negative is not None:negative[k,:n]=v['negative']
                positive,negative,features,keep,mask,coords=[x.cuda() if x is not None else None for x in (positive,negative,features,keep,mask,coords)]
                factor=min((step+1)/spec['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
                for group in optimizer.param_groups:group['lr']=spec['adapter_lr']*factor
                optimizer.zero_grad(set_to_none=True)
                loss,info=native_preference_flow_loss(net,adapter,reference,positive,negative,features,keep,mask,coordinates=coords,generator=rng,beta=spec['beta'],negative_weight=spec['arms'][c['arm']]['negative_weight'])
                loss.backward();norm=torch.nn.utils.clip_grad_norm_(adapter.parameters(),spec['gradient_clip'],error_if_nonfinite=True)
                if not torch.isfinite(loss) or not torch.isfinite(norm) or norm<=0:raise FloatingPointError('Nonfinite or zero training gradient')
                optimizer.step()
                with torch.no_grad():
                    for key,value in adapter.state_dict().items():
                        if value.is_floating_point():ema[key].lerp_(value,1-spec['adapter_ema_decay'])
                m['updates']=step+1;m['training'].append(dict(step=step+1,length=length,batch=batch,ids=ids,loss=float(loss.detach()),gradient_norm=float(norm),learning_rate_factor=factor,
                    positive_sha256=tensor_hash(positive),noise_sha256=tensor_hash(info['noise']),time_sha256=tensor_hash(info['t']),rng_sha256=tensor_hash(rng.get_state()),self_conditioned=info['self_conditioned'],
                    **({} if negative is None else dict(negative_sha256=tensor_hash(negative))),
                    **{k:float(info[k]) for k in ('positive_branch_loss','negative_branch_loss','positive_flow_error','negative_flow_error') if k in info}))
                if (step+1)%10==0:atomic_json(a.output/'manifest.json',m);print('update',step+1,'loss',float(loss.detach()),flush=True)
                del loss,info,positive,negative,features,keep,mask,coords
        torch.cuda.synchronize();m.update(training_seconds=time.monotonic()-start,peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30,generator_final=state_hash(net.state_dict()),reference_final=state_hash(reference.state_dict()),adapter_final=state_hash(adapter.state_dict()))
        if m['peak_reserved_GiB']>75 or m['generator_initial']!=m['generator_final'] or m['reference_initial']!=m['reference_final'] or m['adapter_initial']==m['adapter_final']:raise ValueError('Resource or frozen/update check failed')
        checkpoint=a.output/f'ema_{c["updates"]}.ckpt'
        torch.save(dict(ema={k:v.detach().cpu() for k,v in net.state_dict().items()},fragment_adapter={k:v.cpu() for k,v in ema.items()},raw_fragment_adapter={k:v.detach().cpu() for k,v in adapter.state_dict().items()},reference_fragment_adapter={k:v.detach().cpu() for k,v in reference.state_dict().items()},adapter_config=adapter_config,arch=arch['architecture'],extra_arch=arch['extra_architecture'],model=arch['model'],experiment=c),checkpoint)
        m['checkpoint_sha256']=sha(checkpoint);evaluate(c['updates']);m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
