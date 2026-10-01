"""Matched paired versus independent-noise sampler distillation."""
import argparse,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig,SampleConfig,flow_loss,sample,target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from profile_gpu import Telemetry,atomic_json
from predict import file_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());selection_path=Path(c['selection'])
    if hashlib.sha256(selection_path.read_bytes()).hexdigest()!=c['selection_sha256']:raise ValueError('changed training selection')
    selection=json.loads(selection_path.read_text());a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic()
    m=dict(status='running',config=c,updates=0,training=[],batches=[],scores=[],controls=[],scope='Paired versus independent noise on identical inherited-student endpoints; guidance baked into targets. No new biological state labels or test scoring.');telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        if c['arm'] not in ('reflow_paired','reflow_independent'):raise ValueError('invalid reflow arm')
        if c['updates']<1 or c['evaluation_steps'][-1]!=c['updates']:raise ValueError('invalid update protocol')
        protocol=Path(c['protocol'])
        if file_identity(protocol,hash_contents=True)['sha256']!=c['protocol_sha256']:raise ValueError('changed protocol')
        if not c.get('profile_only'):
            profile=Path(c['profile_result']);capacity=json.loads(profile.read_text())
            if file_identity(profile,hash_contents=True)['sha256']!=c['profile_result_sha256'] or capacity['status']!='complete' or capacity['max_reserved_gib']>110:raise ValueError('capacity gate failed')
        records={};buckets={k:[] for k in (128,256,384,512)}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            for split in ('train','tuning'):
                if set(cache[split])!={r['id'] for r in selection[split]}:raise ValueError('embedding cache coverage mismatch')
                for r in selection[split]:
                    g=cache[split][r['id']]
                    if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence mismatch')
                    original=source['train'][r['id']];records[r['id']]=dict(**r,esm=torch.from_numpy(g['80'][:]),z=torch.from_numpy(original['z'][:]),ca=original['ca_coords'][:])
                    if split=='train':buckets[r['bucket']].append(r['id'])
        covered=set()
        checkpoint_hashes=set()
        for shard in c['pair_shards']:
            path=Path(shard['manifest'])
            if file_identity(path,hash_contents=True)['sha256']!=shard['manifest_sha256']:raise ValueError('pair manifest changed')
            metadata=json.loads(path.read_text());checkpoint_hashes.add(metadata['checkpoint']['sha256'])
            if metadata['status']!='complete' or metadata['config']['protocol_sha256']!=c['protocol_sha256'] or metadata['config']['selection_sha256']!=c['selection_sha256']:raise ValueError('pair provenance mismatch')
            pair_path=path.parent/'pairs.h5'
            if file_identity(pair_path,hash_contents=True)['sha256']!=shard['pairs_sha256']:raise ValueError('pair arrays changed')
            with h5py.File(pair_path) as pairs:
                for ident in pairs:
                    if ident in covered or ident not in {r['id'] for r in selection['train']}:raise ValueError('unexpected/duplicate pair target')
                    covered.add(ident);g=pairs[ident];r=records[ident]
                    if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('pair sequence mismatch')
                    for key in ('noise','endpoint'):
                        value=g[key][:]
                        if value.shape!=(16,r['length'],8) or not np.isfinite(value).all():raise ValueError('invalid pair array')
                        r[key]=torch.from_numpy(value)
                    for k in range(16):
                        expected=target_noise([ident],[r['length']],8,seed=metadata['config']['seed'],sample_index=k)[0]
                        if not torch.equal(r['noise'][k],expected):raise ValueError('recorded seed/noise mismatch')
        if len(checkpoint_hashes)!=1:raise ValueError('mixed teacher checkpoints')
        if not c.get('profile_only') and covered!={r['id'] for r in selection['train']}:raise ValueError('incomplete pair coverage')
        buckets={k:[i for i in ids if i in covered] for k,ids in buckets.items()}
        if any(len(ids)<c['batches'][str(k)] for k,ids in buckets.items()):raise ValueError('too few labeled targets for training batch')
        m['label_controls']=dict(targets=len(covered),pairs=16*len(covered),all_endpoints_retained=True)
        ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';m['checkpoint']=file_identity(ckpt,hash_contents=True)
        if m['checkpoint']['sha256'] not in checkpoint_hashes:raise ValueError('teacher/student initial checkpoint mismatch')
        model,architecture=load_legacy(ckpt,trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
        torch.manual_seed(c['seed']);ema={k:v.detach().clone() for k,v in model.state_dict().items()}
        optimizer=torch.optim.AdamW(model.parameters(),lr=c['learning_rate'],betas=(.9,.95),weight_decay=.01,foreach=False)
        m['trainable_parameters']=sum(p.numel() for p in model.parameters());order=np.random.default_rng(c['seed']);labels_rng=np.random.default_rng(c['seed']+1);rng=torch.Generator(device='cuda').manual_seed(c['seed']);queues={k:[] for k in buckets};telemetry=Telemetry(a.output,True)
        def batch(ids,length,training=False):
            mask=torch.arange(length,device='cuda')[None]<torch.tensor([records[k]['length'] for k in ids],device='cuda')[:,None]
            esm=torch.zeros(len(ids),length,2560,device='cuda');z=torch.zeros(len(ids),length,8,device='cuda');initial=torch.zeros_like(z)
            for i,ident in enumerate(ids):
                r=records[ident];n=r['length'];esm[i,:n]=r['esm'].cuda()
                if training:
                    choice=int(labels_rng.integers(16))
                    z[i,:n]=r['endpoint'][choice].cuda();initial[i,:n]=r['noise'][choice].cuda()
            return esm,mask,z,initial
        def evaluate_at(step,sampling_steps):
            if c.get('evaluation_only'):
                name=f'collect::reflow_eval::{step}::{sampling_steps}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
            model.eval()
            raw={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};model.load_state_dict(ema)
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/f'evaluation_{step}_{sampling_steps}.h5','x') as out:
                for length in buckets:
                    ids=[r['id'] for r in selection['tuning'] if r['bucket']==length]
                    for offset in range(0,len(ids),8):
                        chunk=ids[offset:offset+8];esm,mask,_,_=batch(chunk,length);expanded=esm.repeat_interleave(3,0);masks=mask.repeat_interleave(3,0);noise=torch.zeros(len(chunk)*3,length,8,device='cuda');dn=torch.zeros(len(chunk)*3,4*length,3,device='cuda')
                        for i,ident in enumerate(chunk):
                            n=records[ident]['length']
                            for k in range(3):
                                noise[3*i+k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                                dn[3*i+k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        z=sample(model,expanded,masks,SampleConfig(steps=sampling_steps,guidance=2 if step==0 else 1),noise=noise,conditioning_ids=[ident for ident in chunk for _ in range(3)])
                        _,bb=decoder(z,masks,noise=dn,return_backbone=True);bb=bb.cpu().numpy()
                        if offset==0:
                            n=records[chunk[0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],SampleConfig(steps=sampling_steps,guidance=2 if step==0 else 1),noise=noise[:1,:n]);alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone);m['controls'].append(dict(step=step,sampling_steps=sampling_steps,length=length,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('evaluation batching control failed')
                        for i,ident in enumerate(chunk):
                            r=records[ident];pred=bb[3*i:3*i+3,:r['length']];out.create_dataset(ident,data=pred);geometry=backbone_geometry(pred)
                            for k,x in enumerate(pred):m['scores'].append(dict(step=step,sampling_steps=sampling_steps,target_id=ident,sample=k,**ca_metrics(x[:,1],r['ca']),**{key:float(value[k]) for key,value in geometry.items()}))
            model.load_state_dict(raw);model.train();del raw
            if c.get('evaluation_only'):
                torch.cuda.synchronize();m['batches'].append(dict(nvtx_range=name,step=step,sampling_steps=sampling_steps,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved()));torch.cuda.nvtx.range_pop()
            atomic_json(a.output/'manifest.json',m);print('evaluated',step,sampling_steps,flush=True)
        def evaluate(step):
            for sampling_steps in ([25] if step==0 else c.get('sampling_steps',[5,10])):evaluate_at(step,sampling_steps)
        if not c.get('profile_only'):evaluate(0)
        if c.get('evaluation_only'):
            protocol=Path(c['evaluation_protocol'])
            if file_identity(protocol,hash_contents=True)['sha256']!=c['evaluation_protocol_sha256'] or c['sampling_steps']!=[15,20]:raise ValueError('extension protocol mismatch')
            parent=Path(c['training_manifest']);checkpoint=Path(c['evaluation_checkpoint'])
            if file_identity(parent,hash_contents=True)['sha256']!=c['training_manifest_sha256'] or file_identity(checkpoint,hash_contents=True)['sha256']!=c['evaluation_checkpoint_sha256']:raise ValueError('trained source changed')
            parent_result=json.loads(parent.read_text())
            if parent_result['status']!='complete' or parent_result['updates']!=2000 or parent_result['config']['arm']!=c['arm'] or checkpoint.resolve()!=(parent.parent/'ema_2000.ckpt').resolve():raise ValueError('extension checkpoint does not match its training run')
            trained,_=load_legacy(checkpoint,trusted_pickle=True);model.load_state_dict(trained.state_dict());del trained
            ema={k:v.detach().clone() for k,v in model.state_dict().items()}
            m.update(updates=2000,training_updates_executed=0,scope='Inference-only 15/20-step evaluation of existing 2000-update sampler weights; no additional training.')
            (a.output/'ema_2000.ckpt').symlink_to(checkpoint.resolve());evaluate(2000)
            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('inference extension work cap')
            m['status']='complete';return
        with inference_precision('fp32'):
            for begin,end in zip([0]+c['evaluation_steps'][:-1],c['evaluation_steps']):
                name=f'collect::distill_train::{begin}::{end}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                try:
                    for step in range(begin,end):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('distillation experiment work cap')
                        length=sorted(buckets)[step%4];count=c['batches'][str(length)]
                        if len(queues[length])<count:queues[length]=order.permutation(buckets[length]).tolist()
                        ids=queues[length][:count];del queues[length][:count];esm,mask,z,initial=batch(ids,length,training=True)
                        progress=step/max(c['updates']-1,1);lr=c['learning_rate']*min((step+1)/c['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*progress)));optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
                        loss,_=flow_loss(model,z,esm,mask,FlowConfig(condition_dropout=0,uniform_fraction=.5),generator=rng,initial_noise=initial if c['arm']=='reflow_paired' else None)
                        if not torch.isfinite(loss):raise FloatingPointError('nonfinite training loss')
                        loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
                        if norm<=0:raise FloatingPointError('flow gradient vanished')
                        optimizer.step()
                        with torch.no_grad():
                            values=model.state_dict();keys=[k for k in ema if ema[k].is_floating_point()]
                            torch._foreach_lerp_([ema[k] for k in keys],[values[k] for k in keys],1-c['ema_decay'])
                            for key in ema:
                                if not ema[key].is_floating_point():ema[key].copy_(values[key])
                        m['updates']=step+1
                        if step%25==0 or step+1==end:
                            m['training'].append(dict(step=step+1,length=length,batch=count,flow_loss=float(loss.detach()),gradient_norm=float(norm),learning_rate=lr,ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest()));atomic_json(a.output/'manifest.json',m)
                        del mask,z,esm,initial,loss
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                m['batches'].append(dict(nvtx_range=name,seconds=seconds,updates=end-begin,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                if not c.get('profile_only'):
                    torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},arch=architecture['architecture'],extra_arch=architecture['extra_architecture'],model=architecture['model'],experiment=c),a.output/f'ema_{end}.ckpt');evaluate(end)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
