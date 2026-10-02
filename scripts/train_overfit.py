"""Matched 32-protein teacher-mode learnability and coordinate-frame ablation."""
import argparse,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.backbone import align_backbone_to_reference,encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig,SampleConfig,flow_loss,sample,target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.teacher_states import draw_teacher
from latentfold.training_schedule import proportional_schedule
from latentfold.ensemble_metrics import backbone_geometry
from audit_distill_labels import metrics
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def score_ensemble(bb,record):
    state=record['state'];i,j=[torch.tensor(state[k],device=bb.device) for k in ('i','j')];features=(bb[:,i,1]-bb[:,j,1]).norm(dim=-1)
    ref=torch.tensor(state['features'],device=bb.device,dtype=bb.dtype);dist=(features[:,None]-ref[None]).square().mean(-1).sqrt();error,nearest=dist.min(1)
    selected=torch.tensor(state['teacher_indices'],device=bb.device)[nearest];teacher=record['teacher_backbone'].to(bb.device)[selected];v=metrics(bb,teacher);native=metrics(bb,record['reference_backbone'].to(bb.device)[None].expand(len(bb),-1,-1,-1))
    assigned=torch.tensor(state['clusters'],device=bb.device)[nearest];good=(error<=2)&(v['ca_lddt']>=.8)&v['coarse_valid'];assigned=torch.where(good,assigned,-1)
    assignments=assigned.cpu().numpy();strict_assignments=torch.where(good & (error<=1.),assigned,-1).cpu().numpy();clusters=np.asarray(state['clusters']);p=np.bincount(clusters,minlength=state['states'])/len(clusters);q=np.bincount(assignments[assignments>=0],minlength=state['states'])/len(bb)
    result=dict(strict_coverage={str(k):len(set(strict_assignments[:k])-{-1})/state['states'] for k in (1,4,16,32)},coverage={str(k):len(set(assignments[:k])-{-1})/state['states'] for k in (1,4,16,32)},valid_fraction=v['coarse_valid'].float().mean().item(),teacher_ca_lddt=v['ca_lddt'].mean().item(),reference_ca_lddt=native['ca_lddt'].mean().item(),teacher_feature_rmse=error.mean().item(),valid_teacher_hit_fraction=good.float().mean().item(),state_total_variation=float(.5*(np.abs(p-q).sum()+np.mean(assignments<0))),teacher_sampling_expected_coverage32=float(np.mean(1-(1-p)**32)),assignments=assignments.tolist())
    return result,v,teacher


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());expanded=bool(c.get('corpus_inventory'))
    if expanded:
        if c.get('corpus_kind')=='expansion':
            from expansion_corpus import metadata,load
        else:
            from expanded_corpus import metadata,load
        source=metadata(c)
    else:
        path=Path(c['label_manifest']);source=json.loads(path.read_text())
        if sha(path)!=c['label_manifest_sha256'] or source['status']!='complete' or not source['training_gate_passed'] or sha(path.parent/'labels.h5')!=source['labels_sha256']:raise ValueError('label gate/provenance failed')
    if c['arm'] not in ('reference','aligned_teacher','pca_teacher'):raise ValueError('invalid arm')
    estimator=c.get('target_estimator','sampled')
    if estimator not in ('sampled','posterior') or (estimator=='posterior' and c['arm']=='reference'):raise ValueError('invalid target estimator')
    distribution=c.get('label_distribution','empirical')
    if distribution not in ('empirical','balanced') or (distribution=='balanced' and (c['arm']=='reference' or estimator=='posterior')):raise ValueError('unsupported label distribution/estimator')
    if distribution=='balanced' and sha(c['followup_protocol'])!=c['followup_protocol_sha256']:raise ValueError('balanced protocol changed')
    if c['evaluation_steps'][-1]!=c['updates']:raise ValueError('invalid budget')
    if c.get('local_geometry'):
        recipe=json.loads(Path(c['protocol']).read_text())
        if sha(c['protocol'])!=c['protocol_sha256'] or recipe['local_geometry']!=c['local_geometry'] or not expanded or distribution!='balanced' or c.get('trainable_tail_blocks') is not None or estimator!='sampled':raise ValueError('invalid local geometry scope')
    if not c.get('profile_only'):
        profile=json.loads(Path(c['profile_report']).read_text())
        if sha(c['profile_report'])!=c['profile_report_sha256'] or profile['status']!='complete' or not profile['profile_only'] or profile['max_reserved_gib']>c.get('maximum_profile_gib',110):raise ValueError('capacity gate failed')
    a.output.mkdir(parents=True,exist_ok=False);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,updates=0,training=[],batches=[],scores=[],controls=[],scope=f'{len(source["targets"]) if expanded else 32} training proteins; teacher-mode recall only. No unseen-family or biological-state claim. Original tests untouched.');atomic_json(a.output/'manifest.json',m)
    try:
        records={};buckets={k:[] for k in (128,256,384,512)}
        if expanded:records,buckets=load(c)
        else:
            with h5py.File(path.parent/'labels.h5') as h:
                for r in source['config']['targets']:
                    g=h[r['id']];record=dict(r,state=json.loads(g.attrs['state_definition']))
                    for key in ('esm','reference_z','reference_backbone','teacher_z_aligned','teacher_z_pca','teacher_backbone'):record[key]=torch.from_numpy(g[key][:])
                    record['valid_indices']=np.flatnonzero(g['coarse_valid'][:]);records[r['id']]=record;buckets[r['bucket']].append(r['id'])
        from expansion_corpus import evaluation_records
        evaluation_panel=evaluation_records(records,c)
        summary_protocol=None
        if c.get('summary_arm'):
            from summary_adapter import SummaryAdapter,load_features,condition
            if expanded or c['arm']!='aligned_teacher' or distribution!='balanced' or c.get('local_geometry') or c.get('trainable_tail_blocks') is not None:raise ValueError('invalid summary learning scope')
            summary_protocol=load_features(c,records)
            if c['seed'] not in (summary_protocol['first_seed'],summary_protocol['replication_seed']):raise ValueError('undeclared summary seed')
            if c['updates']!=(summary_protocol['profile']['updates'] if c.get('profile_only') else summary_protocol['updates']):raise ValueError('undeclared summary budget')
        m['training_targets']=len(records);m['evaluated_targets']=len(evaluation_panel)
        lengths=[sorted(buckets)[step%4] for step in range(c['updates'])]
        if expanded and not c.get('profile_only'):
            lengths=proportional_schedule({k:len(v) for k,v in buckets.items()},c['updates'],c['seed']+2)
        if expanded:m['length_schedule']=lengths
        ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';m['initial_checkpoint_sha256']=sha(ckpt)
        if c.get('checkpoint_sha256') and c['checkpoint_sha256']!=m['initial_checkpoint_sha256']:raise ValueError('initial checkpoint changed')
        model,architecture=load_legacy(ckpt,trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        if c.get('trainable_tail_blocks') is not None:
            from latentfold.training_subset import configure_tail,frozen_digest
            m['training_subset']=configure_tail(model,c['trainable_tail_blocks'])
            m['training_subset']['initial_frozen_sha256']=frozen_digest(model)
        trainable=[p for p in model.parameters() if p.requires_grad]
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=c['decoder_steps']).cuda()
        torch.manual_seed(c['seed'])
        parameters=trainable
        if summary_protocol:
            adapter=summary_protocol['adapter'];model.summary_adapter=SummaryAdapter(adapter['width'],adapter['bound']).cuda()
            adapter_parameters=list(model.summary_adapter.parameters());parameters=[dict(params=trainable),dict(params=adapter_parameters,lr=adapter['learning_rate'])];trainable=trainable+adapter_parameters
            m['summary_adapter']=dict(parameters=sum(p.numel() for p in adapter_parameters),arm=c['summary_arm'],initial_sha256=hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for v in model.summary_adapter.state_dict().values())).hexdigest(),controls=[])
            with torch.no_grad():
                for length in buckets:
                    ident=buckets[length][0];r=records[ident];n=r['length'];x=torch.zeros(1,length,2560,device='cuda');x[0,:n]=r['esm'].cuda();mask=torch.arange(length,device='cuda')[None]<n
                    exact=torch.equal(condition(model,records,[ident],x,mask),x);m['summary_adapter']['controls'].append(dict(bucket=length,initial_exact=exact))
                    if not exact:raise ValueError('summary adapter changes initial condition')
        ema={k:v.detach().clone() for k,v in model.state_dict().items()};optimizer=torch.optim.AdamW(parameters,lr=c['learning_rate'],betas=(.9,.95),weight_decay=.01,foreach=False)
        order=np.random.default_rng(c['seed']);labels_rng=np.random.default_rng(c['seed']+1);rng=torch.Generator(device='cuda').manual_seed(c['seed']);queues={k:[] for k in buckets};telemetry=Telemetry(a.output,True)
        def evaluate(step):
            model.eval();raw={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};model.load_state_dict(ema);state_cpu=torch.get_rng_state();state_gpu=torch.cuda.get_rng_state();evaluated_controls=set()
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/f'evaluation_{step}.h5','x') as out:
                for index,(ident,r) in enumerate(evaluation_panel.items()):
                    n=r['length'];length=r['bucket'];esm=torch.zeros(1,length,2560,device='cuda');esm[0,:n]=r['esm'].cuda();mask=torch.arange(length,device='cuda')[None]<n
                    if summary_protocol:esm=condition(model,records,[ident],esm,mask)
                    noise=torch.zeros(32,length,8,device='cuda');dn=torch.zeros(32,4*length,3,device='cuda')
                    for k in range(32):
                        noise[k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0];dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                    for guidance in c.get('evaluation_guidance',(1,2)):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('overfit evaluation cap')
                        name=f'collect::overfit_eval::{step}::{index}::{guidance}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                        try:
                            z=sample(model,esm.repeat(32,1,1),mask.repeat(32,1),SampleConfig(steps=25,guidance=guidance),noise=noise,conditioning_ids=[ident]*32);_,bb=decoder(z,mask.repeat(32,1),noise=dn,return_backbone=True);bb=bb[:,:n];scored,values,teacher=score_ensemble(bb,r)
                            # Diagnostic only: reference alignment never changes generated samples.
                            aligned=align_backbone_to_reference(bb,r['reference_backbone'].cuda(),torch.ones(n,dtype=torch.bool,device='cuda'))
                            latent_mask=torch.ones(32,n,dtype=torch.bool,device='cuda');reencoded=encode_backbone(decoder,bb,latent_mask);aligned_z=encode_backbone(decoder,aligned,latent_mask);teacher_z=r['teacher_z_aligned'][r['valid_indices']].cuda()
                            def nearest_rmse(values):return ((values[:,None]-teacher_z[None]).square().mean((2,3))).sqrt().min(1).values.mean().item()
                            scored['latent_diagnostic']=dict(sampled_to_teacher_rmse=nearest_rmse(z[:,:n]),reencoded_to_teacher_rmse=nearest_rmse(reencoded),pose_aligned_reencoded_to_teacher_rmse=nearest_rmse(aligned_z),decoder_encoder_rmse=(reencoded-z[:,:n]).square().mean().sqrt().item())
                            del aligned,latent_mask,reencoded,aligned_z,teacher_z
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
                        length=lengths[step];count=c['batches'][str(length)]
                        while len(queues[length])<count:queues[length].extend(order.permutation(buckets[length]).tolist())
                        ids=queues[length][:count];del queues[length][:count];esm=torch.zeros(count,length,2560,device='cuda');z=torch.zeros(count,length,8,device='cuda');mask=torch.arange(length,device='cuda')[None]<torch.tensor([records[i]['length'] for i in ids],device='cuda')[:,None];choices=[]
                        for k,ident in enumerate(ids):
                            r=records[ident];n=r['length'];choice=draw_teacher(r['valid_indices'],r['state'],labels_rng.random(),distribution);choices.append(choice);esm[k,:n]=r['esm'].cuda();target=r['reference_z'] if c['arm']=='reference' else r['teacher_z_aligned' if c['arm']=='aligned_teacher' else 'teacher_z_pca'][choice];z[k,:n]=target.cuda()
                        posterior_args={}
                        if estimator=='posterior':
                            key='teacher_z_aligned' if c['arm']=='aligned_teacher' else 'teacher_z_pca';teachers=max(len(records[i]['valid_indices']) for i in ids)
                            bank=torch.zeros(count,teachers,length,8,device='cuda');valid=torch.zeros(count,teachers,device='cuda',dtype=torch.bool)
                            for k,ident in enumerate(ids):
                                r=records[ident];indices=r['valid_indices'];bank[k,:len(indices),:r['length']]=r[key][indices].cuda();valid[k,:len(indices)]=True
                            posterior_args=dict(teacher_bank=bank,teacher_valid=valid)
                        progress=step/max(c['updates']-1,1);lr=c['learning_rate']*min((step+1)/c['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*progress)));optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
                        if summary_protocol:
                            optimizer.param_groups[1]['lr']=lr*summary_protocol['adapter']['learning_rate']/c['learning_rate']
                            esm=condition(model,records,ids,esm,mask)
                        loss,info=flow_loss(model,z,esm,mask,FlowConfig(),generator=rng,return_state=True,**posterior_args)
                        if not torch.isfinite(loss):raise FloatingPointError('nonfinite loss')
                        if c.get('local_geometry'):
                            from latentfold.local_geometry import endpoint_geometry
                            from latentfold.training import controlled_backward
                            auxiliary,aux_stats=endpoint_geometry(decoder,info['state'],ids,[records[i]['length'] for i in ids],c['local_geometry'],step)
                            aux_stats.update(controlled_backward(model,loss,auxiliary,weight=c['local_geometry']['weight'],max_ratio=c['local_geometry']['maximum_gradient_ratio'],loss_scale=1.))
                            m.setdefault('local_geometry_updates',[]).append(dict(step=step+1,length=length,**aux_stats))
                            del auxiliary,aux_stats
                        else:loss.backward()
                        if summary_protocol:
                            adapter_norm=torch.stack([p.grad.detach().square().sum() for p in model.summary_adapter.parameters() if p.grad is not None]).sum().sqrt()
                            if not torch.isfinite(adapter_norm) or adapter_norm<=0:raise FloatingPointError('summary adapter gradient vanished')
                            m['summary_adapter'].setdefault('gradients',[]).append(dict(step=step+1,bucket=length,norm=float(adapter_norm)))
                        norm=torch.nn.utils.clip_grad_norm_(trainable,1.,error_if_nonfinite=True)
                        if norm<=0:raise FloatingPointError('zero gradient')
                        optimizer.step()
                        with torch.no_grad():
                            values=model.state_dict();keys=[k for k in ema if ema[k].is_floating_point()];torch._foreach_lerp_([ema[k] for k in keys],[values[k] for k in keys],1-c['ema_decay'])
                            for key in ema:
                                if not ema[key].is_floating_point():ema[key].copy_(values[key])
                        m['updates']=step+1
                        if step%25==0 or step+1==end:
                            state=info['state'];times=state['t'].detach();target_velocity=(z-state['x'].detach())/(1-times[:,None,None]);per_protein=(((state['velocity'].detach()-target_velocity)**2).mean(-1)*mask).sum(1)/mask.sum(1)
                            bins={f'{lo}_{hi}':dict(count=int(((times>=lo)&(times<hi)).sum()),mse=float(per_protein[(times>=lo)&(times<hi)].mean()) if ((times>=lo)&(times<hi)).any() else None) for lo,hi in ((0.,.1),(.1,.25),(.25,.5),(.5,.75),(.75,.9),(.9,1.))}
                            m['training'].append(dict(time_bins=bins,step=step+1,length=length,batch=count,flow_loss=float(loss.detach()),gradient_norm=float(norm),learning_rate=lr,ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest(),label_choices_sha256=hashlib.sha256(np.asarray(choices,dtype='int64').tobytes()).hexdigest()));atomic_json(a.output/'manifest.json',m)
                            if estimator=='posterior':
                                m['training'][-1]['posterior_variance']=float(info['posterior_variance'].mean());atomic_json(a.output/'manifest.json',m)
                            del state,times,target_velocity,per_protein,bins
                        del mask,z,esm,loss,info
                        if estimator=='posterior':del bank,valid
                        del posterior_args
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                m['batches'].append(dict(nvtx_range=name,stage='training',seconds=seconds,updates=end-begin,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                if c.get('trainable_tail_blocks') is not None:
                    subset=m['training_subset'];subset['final_frozen_sha256']=frozen_digest(model);subset['ema_frozen_sha256']=frozen_digest(model,ema)
                    subset['frozen_unchanged']=subset['initial_frozen_sha256']==subset['final_frozen_sha256']==subset['ema_frozen_sha256']
                    subset['verified_update']=end
                    if not subset['frozen_unchanged']:raise ValueError('frozen parameters changed')
                if not c.get('profile_only'):
                    torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},arch=architecture['architecture'],extra_arch=architecture['extra_architecture'],model=architecture['model'],experiment=c),a.output/f'ema_{end}.ckpt');evaluate(end)
        if c.get('trainable_tail_blocks') is not None:
            subset=m['training_subset'];subset['final_frozen_sha256']=frozen_digest(model);subset['ema_frozen_sha256']=frozen_digest(model,ema)
            subset['frozen_unchanged']=subset['initial_frozen_sha256']==subset['final_frozen_sha256']==subset['ema_frozen_sha256']
            if not subset['frozen_unchanged']:raise ValueError('frozen parameters changed')
        m['status']='complete'
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
