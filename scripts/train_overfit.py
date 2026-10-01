"""Matched 32-protein teacher-mode learnability and coordinate-frame ablation."""
import argparse,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig,SampleConfig,flow_loss,sample,target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from audit_distill_labels import metrics
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def score_ensemble(bb,record):
    state=record['state'];i,j=[torch.tensor(state[k],device=bb.device) for k in ('i','j')];features=(bb[:,i,1]-bb[:,j,1]).norm(dim=-1)
    ref=torch.tensor(state['features'],device=bb.device,dtype=bb.dtype);dist=(features[:,None]-ref[None]).square().mean(-1).sqrt();error,nearest=dist.min(1)
    selected=torch.tensor(state['teacher_indices'],device=bb.device)[nearest];teacher=record['teacher_backbone'].to(bb.device)[selected];v=metrics(bb,teacher);native=metrics(bb,record['reference_backbone'].to(bb.device)[None].expand(len(bb),-1,-1,-1))
    assigned=torch.tensor(state['clusters'],device=bb.device)[nearest];good=(error<=2)&(v['ca_lddt']>=.8)&v['coarse_valid'];assigned=torch.where(good,assigned,-1)
    assignments=assigned.cpu().numpy();clusters=np.asarray(state['clusters']);p=np.bincount(clusters,minlength=state['states'])/len(clusters);q=np.bincount(assignments[assignments>=0],minlength=state['states'])/len(bb)
    result=dict(coverage={str(k):len(set(assignments[:k])-{-1})/state['states'] for k in (1,4,16,32)},valid_fraction=v['coarse_valid'].float().mean().item(),teacher_ca_lddt=v['ca_lddt'].mean().item(),reference_ca_lddt=native['ca_lddt'].mean().item(),teacher_feature_rmse=error.mean().item(),valid_teacher_hit_fraction=good.float().mean().item(),state_total_variation=float(.5*(np.abs(p-q).sum()+np.mean(assignments<0))),teacher_sampling_expected_coverage32=float(np.mean(1-(1-p)**32)),assignments=assignments.tolist())
    return result,v,teacher


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['label_manifest']);source=json.loads(path.read_text())
    if sha(path)!=c['label_manifest_sha256'] or source['status']!='complete' or not source['training_gate_passed'] or sha(path.parent/'labels.h5')!=source['labels_sha256']:raise ValueError('label gate/provenance failed')
    if c['arm'] not in ('reference','aligned_teacher','pca_teacher'):raise ValueError('invalid arm')
    if c['evaluation_steps'][-1]!=c['updates']:raise ValueError('invalid budget')
    if not c.get('profile_only'):
        profile=json.loads(Path(c['profile_report']).read_text())
        if sha(c['profile_report'])!=c['profile_report_sha256'] or profile['status']!='complete' or not profile['profile_only'] or profile['max_reserved_gib']>110:raise ValueError('capacity gate failed')
    a.output.mkdir(parents=True,exist_ok=False);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,updates=0,training=[],batches=[],scores=[],controls=[],scope='32 training proteins; teacher-mode recall only. No unseen-family or biological-state claim. Original tests untouched.');atomic_json(a.output/'manifest.json',m)
    try:
        records={};buckets={k:[] for k in (128,256,384,512)}
        with h5py.File(path.parent/'labels.h5') as h:
            for r in source['config']['targets']:
                g=h[r['id']];record=dict(r,state=json.loads(g.attrs['state_definition']))
                for key in ('esm','reference_z','reference_backbone','teacher_z_aligned','teacher_z_pca','teacher_backbone'):record[key]=torch.from_numpy(g[key][:])
                record['valid_indices']=np.flatnonzero(g['coarse_valid'][:]);records[r['id']]=record;buckets[r['bucket']].append(r['id'])
        ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';m['initial_checkpoint_sha256']=sha(ckpt)
        model,architecture=load_legacy(ckpt,trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=c['decoder_steps']).cuda()
        torch.manual_seed(c['seed']);ema={k:v.detach().clone() for k,v in model.state_dict().items()};optimizer=torch.optim.AdamW(model.parameters(),lr=c['learning_rate'],betas=(.9,.95),weight_decay=.01,foreach=False)
        order=np.random.default_rng(c['seed']);labels_rng=np.random.default_rng(c['seed']+1);rng=torch.Generator(device='cuda').manual_seed(c['seed']);queues={k:[] for k in buckets};telemetry=Telemetry(a.output,True)
        def evaluate(step):
            model.eval();raw={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};model.load_state_dict(ema);state_cpu=torch.get_rng_state();state_gpu=torch.cuda.get_rng_state();evaluated_controls=set()
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/f'evaluation_{step}.h5','x') as out:
                for index,(ident,r) in enumerate(records.items()):
                    n=r['length'];length=r['bucket'];esm=torch.zeros(1,length,2560,device='cuda');esm[0,:n]=r['esm'].cuda();mask=torch.arange(length,device='cuda')[None]<n
                    noise=torch.zeros(32,length,8,device='cuda');dn=torch.zeros(32,4*length,3,device='cuda')
                    for k in range(32):
                        noise[k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0];dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                    for guidance in (1,2):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('overfit evaluation cap')
                        name=f'collect::overfit_eval::{step}::{index}::{guidance}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                        try:
                            z=sample(model,esm.repeat(32,1,1),mask.repeat(32,1),SampleConfig(steps=25,guidance=guidance),noise=noise,conditioning_ids=[ident]*32);_,bb=decoder(z,mask.repeat(32,1),noise=dn,return_backbone=True);bb=bb[:,:n];scored,values,teacher=score_ensemble(bb,r)
                            if step==0 and (length,guidance) not in evaluated_controls:
                                single=sample(model,esm[:,:n],mask[:,:n],SampleConfig(steps=25,guidance=guidance),noise=noise[:1,:n]);alone=decoder(single,mask[:,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:,1].cpu().numpy(),alone)
                                cpu=ca_metrics(bb[0,:,1].cpu().numpy(),teacher[0,:,1].cpu().numpy());valid=backbone_geometry(bb.cpu().numpy())['coarse_valid']
                                if control['ca_rmsd']>.2 or control['ca_lddt']<.99 or abs(cpu['ca_lddt']-values['ca_lddt'][0].item())>1e-5 or not np.array_equal(valid,values['coarse_valid'].cpu().numpy()):raise ValueError('batch/metric control failed')
                                m['controls'].append(dict(bucket=length,guidance=guidance,**control));evaluated_controls.add((length,guidance))
                            g=out.require_group(ident).create_group(f'cfg{guidance}');g.create_dataset('backbone',data=bb.cpu().numpy());g.create_dataset('z',data=z[:,:n].cpu().numpy());m['scores'].append(dict(step=step,target_id=ident,guidance=guidance,**scored));torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,stage='evaluation',seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    atomic_json(a.output/'manifest.json',m)
            torch.set_rng_state(state_cpu);torch.cuda.set_rng_state(state_gpu);model.load_state_dict(raw);model.train();del raw;print('evaluated',step,flush=True)
        if not c.get('profile_only'):evaluate(0)
        with inference_precision('fp32'):
            for begin,end in zip([0]+c['evaluation_steps'][:-1],c['evaluation_steps']):
                name=f'collect::overfit_train::{begin}::{end}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                try:
                    for step in range(begin,end):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('overfit training cap')
                        length=sorted(buckets)[step%4];count=c['batches'][str(length)]
                        while len(queues[length])<count:queues[length].extend(order.permutation(buckets[length]).tolist())
                        ids=queues[length][:count];del queues[length][:count];esm=torch.zeros(count,length,2560,device='cuda');z=torch.zeros(count,length,8,device='cuda');mask=torch.arange(length,device='cuda')[None]<torch.tensor([records[i]['length'] for i in ids],device='cuda')[:,None];choices=[]
                        for k,ident in enumerate(ids):
                            r=records[ident];n=r['length'];choice=int(r['valid_indices'][int(labels_rng.random()*len(r['valid_indices']))]);choices.append(choice);esm[k,:n]=r['esm'].cuda();target=r['reference_z'] if c['arm']=='reference' else r['teacher_z_aligned' if c['arm']=='aligned_teacher' else 'teacher_z_pca'][choice];z[k,:n]=target.cuda()
                        progress=step/max(c['updates']-1,1);lr=c['learning_rate']*min((step+1)/c['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*progress)));optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
                        loss,_=flow_loss(model,z,esm,mask,FlowConfig(),generator=rng)
                        if not torch.isfinite(loss):raise FloatingPointError('nonfinite loss')
                        loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
                        if norm<=0:raise FloatingPointError('zero gradient')
                        optimizer.step()
                        with torch.no_grad():
                            values=model.state_dict();keys=[k for k in ema if ema[k].is_floating_point()];torch._foreach_lerp_([ema[k] for k in keys],[values[k] for k in keys],1-c['ema_decay'])
                            for key in ema:
                                if not ema[key].is_floating_point():ema[key].copy_(values[key])
                        m['updates']=step+1
                        if step%25==0 or step+1==end:
                            m['training'].append(dict(step=step+1,length=length,batch=count,flow_loss=float(loss.detach()),gradient_norm=float(norm),learning_rate=lr,ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest(),label_choices_sha256=hashlib.sha256(np.asarray(choices,dtype='int64').tobytes()).hexdigest()));atomic_json(a.output/'manifest.json',m)
                        del mask,z,esm,loss
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                m['batches'].append(dict(nvtx_range=name,stage='training',seconds=seconds,updates=end-begin,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                if not c.get('profile_only'):
                    torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},arch=architecture['architecture'],extra_arch=architecture['extra_architecture'],model=architecture['model'],experiment=c),a.output/f'ema_{end}.ckpt');evaluate(end)
        m['status']='complete'
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
