"""Matched adapter-only/full training on explicitly isolated fragment inputs."""
import argparse,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.generative import sample_unconditional
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,fragment_flow_loss,sample_fragment
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter,fragment_coordinates
from latentfold.unconditional_training import freeze_unused_conditioning
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from train_unconditional_reflow import frozen_hash
from generate_generative_pilot import motif_error
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def digest(x):return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def load_data(path):
    data={}
    with h5py.File(path) as f:
        for cohort in ('train','development'):
            for ident,g in f[cohort].items():
                n=int(g.attrs['length']);conditions={}
                for name,q in g['conditions'].items():
                    features,keep=fragment_features(torch.from_numpy(q['latent'][:]),q.attrs['sequence'],length=n,start=int(q.attrs['start']))
                    conditions[name]=dict(features=features,keep=keep,fragment=q['fragment'][:],coordinates=fragment_coordinates(torch.from_numpy(q['fragment'][:]),length=n,start=int(q.attrs['start'])))
                data[(cohort,ident)]=dict(length=n,family=g.attrs['family'],conditions=conditions,target=torch.from_numpy(g['reference_z'][:]) if cohort=='train' else None,reference=g['reference_backbone'][:] if cohort=='train' else None)
    return data


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','data_report','data_manifest','fragments','checkpoint','decoder_checkpoint','initial_manifest','initial_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    warm=c.get('warm_start',False)
    if warm:
        for key in ('warm_protocol','warm_parent_manifest','warm_parent_report','warm_predictions'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed warm-start source')
        if c['arm']!='full' or c.get('variant')!='geometry' or c.get('auxiliary_motif') or c.get('total_prior_updates')!=2000:raise ValueError('Wrong warm-start arm')
    if c.get('expanded_fragment_data'):
        if not warm or sha(c['expanded_protocol'])!=c['expanded_protocol_sha256']:raise ValueError('Invalid expanded continuation')
        parent_config=json.loads(Path(c['warm_parent_manifest']).read_text())['config']
        with h5py.File(parent_config['fragments']) as original:
            if sorted(original['train'])!=c['evaluation_train_ids']:raise ValueError('Changed original capacity panel')
    geometry=c.get('variant')=='geometry'
    if c.get('distance_precision')=='fp64':
        if not geometry or sha(c['geometry_precision_protocol'])!=c['geometry_precision_protocol_sha256'] or sha(c['pose_diagnostic_report'])!=c['pose_diagnostic_report_sha256'] or not json.loads(Path(c['pose_diagnostic_report']).read_text())['corrected_precision_profile_qualified']:raise ValueError('Unqualified precision correction')
    if c.get('auxiliary_motif'):
        if not geometry or c['arm']!='adapter_only' or c.get('distance_precision')!='fp64' or sha(c['motif_objective_protocol'])!=c['motif_objective_protocol_sha256'] or sha(c['motif_baseline_report'])!=c['motif_baseline_report_sha256']:raise ValueError('Unqualified motif objective recipe')
        expected=json.loads(Path(c['motif_objective_protocol']).read_text())['auxiliary']
        if c['auxiliary_motif']!=expected:raise ValueError('Changed motif objective parameters')
    if geometry:
        for baseline in c['baseline_reports']:
            if sha(baseline['path'])!=baseline['sha256']:raise ValueError('Changed baseline evidence')
    if geometry and sha(c['geometry_protocol'])!=c['geometry_protocol_sha256']:raise ValueError('Changed geometry recipe')
    if geometry and c['arm']!='adapter_only':
        if c['arm']!='full' or c.get('auxiliary_motif'):raise ValueError('Undeclared geometry arm')
        for key in ('geometry_full_protocol','geometry_frozen_report','geometry_designability_report'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed full geometry prerequisite')
    recipe=json.loads(Path(c['protocol']).read_text());dr=json.loads(Path(c['data_report']).read_text())
    if not dr['training_gate_passed'] or c['arm'] not in recipe['arms'] or c['seed']!=(json.loads(Path(c['warm_protocol']).read_text())['seed'] if warm else recipe['seed']) or c['batches']!=recipe['batches']:raise ValueError('Wrong recipe or data gate')
    if c['updates']!=(40 if c['profile_only'] else 2000) or c['evaluation_steps']!=([40] if c['profile_only'] else [500,2000]):raise ValueError('Wrong update schedule')
    if not c['profile_only']:
        if sha(c['profile_report'])!=c['profile_report_sha256'] or not json.loads(Path(c['profile_report']).read_text())['profile_qualified']:raise ValueError('Profile not qualified')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,updates=0,training=[],batches=[],evaluations=[],initial_controls=[],sampling_controls=[],geometry_controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);data=load_data(c['fragments'])
        model,arch=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True
        if c['arm']=='adapter_only':model.requires_grad_(False);frozen=[n for n,_ in model.named_parameters()]
        else:frozen=freeze_unused_conditioning(model)
        torch.manual_seed(c['seed']);adapter=(FragmentGeometryAdapter(model.d_model,n_layers=len(model.blocks),n_heads=model.n_heads,hidden=recipe['adapter']['hidden'],distance_precision=c.get('distance_precision','fp32')) if geometry else FragmentAdapter(model.d_model,recipe['adapter']['hidden'])).cuda().train()
        if warm:
            parent_checkpoint=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True);adapter.load_state_dict(parent_checkpoint['fragment_adapter']);del parent_checkpoint
        m['frozen_names']=frozen;m['frozen_initial']=frozen_hash(model,frozen);m['adapter_initial']=frozen_hash(adapter,[n for n,_ in adapter.named_parameters()]);m['token_adapter_initial']=frozen_hash(adapter,['hidden.weight','hidden.bias','output.weight','output.bias'])
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        ema={k:v.detach().clone() for k,v in model.state_dict().items()};adapter_ema={k:v.detach().clone() for k,v in adapter.state_dict().items()}
        trunk=[p for p in model.parameters() if p.requires_grad];aps=list(adapter.parameters());parameters=trunk+aps;groups=[dict(params=aps,lr=3e-4,base_lr=3e-4)]
        if trunk:groups.append(dict(params=trunk,lr=1e-5,base_lr=1e-5))
        optimizer=torch.optim.AdamW(groups,betas=(.9,.95),weight_decay=.01,foreach=False);order=np.random.default_rng(c['seed']);rng=torch.Generator(device='cuda').manual_seed(c['seed']);torch.cuda.manual_seed(c['seed']);m['trainable_parameters']=sum(p.numel() for p in parameters);telemetry=Telemetry(a.output,True)
        bucket_ids={n:sorted(ident for (cohort,ident),v in data.items() if cohort=='train' and (v['length']+127)//128*128==n) for n in (128,256,384,512)}
        def evaluate(step):
            saved_rng=torch.cuda.get_rng_state();raw={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};araw={k:v.detach().cpu().clone() for k,v in adapter.state_dict().items()};model.load_state_dict(ema);adapter.load_state_dict(adapter_ema);model.eval();adapter.eval();tick=time.monotonic();scores=[]
            keys=[key for key in sorted(data) if (not c['profile_only'] or key[0]=='development' and key[1] in c['control_ids']) and (key[0]!='train' or 'evaluation_train_ids' not in c or key[1] in c['evaluation_train_ids'])]
            with torch.no_grad(),inference_precision('fp32'),h5py.File(c['initial_predictions']) as initial,h5py.File(c['warm_predictions'] if warm else c['initial_predictions']) as historical,h5py.File(a.output/f'evaluation_{step}.h5','x') as out:
                for cohort,ident in keys:
                    v=data[(cohort,ident)];q=v['conditions']['f30_center'];n=v['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');features=q['features'][None].expand(4,-1,-1).cuda();keep=q['keep'][None].expand(4,-1).cuda();seed=2026100211 if cohort=='development' else 2026100232
                    noise=torch.cat([target_noise([ident],[n],8,seed=seed,sample_index=k,stream='flow:0',device='cuda') for k in range(4)]);dn=torch.cat([target_noise([ident],[4*n],3,seed=seed,sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                    coordinates=q['coordinates'][None].expand(4,-1,-1).cuda() if geometry else None
                    reference=v['reference'] if cohort=='train' else initial['references/'+ident+'/backbone'][:]
                    for mode in ('conditioned','null'):
                        z=sample_fragment(model,adapter,features,keep,mask,noise=noise,steps=50,drop_fragment=mode=='null',coordinates=coordinates);_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();geom=backbone_geometry(bb);fragment_bb=bb[:,q['keep'].numpy()];errors=motif_error(fragment_bb,q['fragment'],np.ones(len(q['fragment']),bool));g=out.create_group(f'{cohort}/{mode}/{ident}');g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=z.cpu().numpy())
                        if not np.isfinite(bb).all():raise ValueError('Nonfinite decoded samples')
                        if step==0 and (cohort=='development' or warm):
                            history_path=f'{cohort}/{mode}/{ident}' if warm else 'original50/unconditional/'+ident
                            expected=historical[history_path+'/backbone'][:];ez=historical[history_path+'/latent'][:];ev=backbone_geometry(expected)['coarse_valid']
                            for k in range(4):
                                control=dict(target_id=ident,mode=mode,slot=k,latent_max_abs=float(np.max(abs(z[k].cpu().numpy()-ez[k]))),validity_identical=bool(ev[k]==geom['coarse_valid'][k]),**ca_metrics(bb[k,:,1],expected[k,:,1]));m.setdefault('warm_controls',[]).append(dict(cohort=cohort,**control)) if warm else None
                                if cohort=='development':m['initial_controls'].append(control)
                                if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.2 or control['ca_lddt']<.99 or not control['validity_identical']:raise ValueError('Historical null parity failed')
                        if step==0 and mode=='conditioned' and ident in c['control_ids']:
                            esm=features.new_zeros(1,n,model.cond_norm.normalized_shape[0]);original=torch.from_numpy(historical[f'{cohort}/{mode}/{ident}/latent'][:1]).cuda() if warm else sample_unconditional(model,esm,mask[:1],noise=noise[:1],steps=50);single=sample_fragment(model,adapter,features[:1],keep[:1],mask[:1],noise=noise[:1],coordinates=coordinates[:1] if geometry else None);control=dict(target_id=ident,original_max_abs=float((original-(z[:1] if warm else single)).abs().max()),batched_max_abs=float((single-z[:1]).abs().max()));m['sampling_controls'].append(control)
                            if control['original_max_abs']>1e-5 or control['batched_max_abs']>1e-4:raise ValueError('Initial sampler/batch control failed')
                        if geometry and mode=='conditioned' and ident in c['control_ids']:
                            cc=coordinates.double() if c.get('distance_precision')=='fp64' else coordinates;rotations=[('quarter',cc.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]))]
                            if c.get('distance_precision')=='fp64':
                                qr=np.linalg.qr(np.random.default_rng(2026100234).normal(size=(3,3)))[0]
                                if np.linalg.det(qr)<0:qr[:,0]*=-1
                                rotations.append(('general',cc.new_tensor(qr)))
                            for kind,rotation in rotations:
                                posed=(cc@rotation+cc.new_tensor([11,7,-3]))*keep[...,None];other=sample_fragment(model,adapter,features,keep,mask,noise=noise,steps=50,coordinates=posed);control=dict(step=step,target_id=ident,pose_kind=kind,pose_latent_max_abs=float((other-z).abs().max()));m['geometry_controls'].append(control)
                                if control['pose_latent_max_abs']>1e-4:raise ValueError('Geometry conditioner pose dependence')
                        scores.extend(dict(cohort=cohort,mode=mode,target_id=ident,family=v['family'],slot=k,motif_drms=float(errors[k]),coarse_valid=int(geom['coarse_valid'][k]),**ca_metrics(bb[k,:,1],reference[:,1])) for k in range(4))
                    out.flush();atomic_json(a.output/'manifest.json',m)
            m['evaluations'].append(dict(step=step,scores=scores,seconds=time.monotonic()-tick));model.load_state_dict(raw);adapter.load_state_dict(araw);model.train();adapter.train();torch.cuda.set_rng_state(saved_rng);del raw,araw;atomic_json(a.output/'manifest.json',m)
        evaluate(0)
        with inference_precision('fp32'):
            for begin,end in zip([0]+c['evaluation_steps'][:-1],c['evaluation_steps']):
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                for step in range(begin,end):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Fragment training cap')
                    n=(128,256,384,512)[step%4];b=c['batches'][str(n)];ids=order.choice(bucket_ids[n],size=b).tolist();names=[order.choice(sorted(data[('train',ident)]['conditions'])) for ident in ids];z=torch.zeros(b,n,8);features=torch.zeros(b,n,29);keep=torch.zeros(b,n,dtype=torch.bool);mask=torch.zeros_like(keep);coordinates=torch.zeros(b,n,3) if geometry else None
                    for i,(ident,name) in enumerate(zip(ids,names)):
                        v=data[('train',ident)];q=v['conditions'][name];l=v['length'];z[i,:l]=v['target'];features[i,:l]=q['features'];keep[i,:l]=q['keep'];mask[i,:l]=True
                        if geometry:coordinates[i,:l]=q['coordinates']
                    coordinates=coordinates.cuda() if geometry else None
                    z,features,keep,mask=[x.cuda() for x in (z,features,keep,mask)];factor=min((step+1)/100,1)*(.1+.9*.5*(1+math.cos(math.pi*step/1999)))
                    for group in optimizer.param_groups:group['lr']=group['base_lr']*factor
                    optimizer.zero_grad(set_to_none=True);loss,info=fragment_flow_loss(model,adapter,z,features,keep,mask,generator=rng,coordinates=coordinates,return_state=bool(c.get('auxiliary_motif')))
                    if c.get('auxiliary_motif'):
                        from latentfold.fragment_objective import endpoint_fragment_objective
                        from latentfold.training import controlled_backward
                        recipe_aux=c['auxiliary_motif'];cpu_rng=torch.get_rng_state();cuda_rng=torch.cuda.get_rng_state();auxiliary,stats=endpoint_fragment_objective(decoder,info['state'],ids,[data[('train',i)]['length'] for i in ids],coordinates,keep,step=step,seed=recipe_aux['seed'],maximum_examples=recipe_aux['maximum_examples'],minimum_time=recipe_aux['minimum_time'],maximum_time=recipe_aux['maximum_time']);torch.set_rng_state(cpu_rng);torch.cuda.set_rng_state(cuda_rng);stats.update(controlled_backward(adapter,loss,auxiliary,weight=recipe_aux['maximum_weight'],max_ratio=recipe_aux['maximum_gradient_ratio'],loss_scale=1.));m.setdefault('motif_objective_updates',[]).append(dict(step=step+1,**stats));del auxiliary,stats
                    else:loss.backward()
                    anorm=torch.linalg.vector_norm(torch.stack([p.grad.norm() for p in aps if p.grad is not None]));norm=torch.nn.utils.clip_grad_norm_(parameters,1.,error_if_nonfinite=True)
                    if not torch.isfinite(loss) or not torch.isfinite(anorm) or anorm<=0 or norm<=0:raise FloatingPointError('Invalid flow loss/adapter gradient')
                    optimizer.step()
                    with torch.no_grad():
                        for net,bank in ((model,ema),(adapter,adapter_ema)):
                            current=net.state_dict();keys=[k for k in bank if bank[k].is_floating_point()];torch._foreach_lerp_([bank[k] for k in keys],[current[k] for k in keys],.01)
                    m['updates']=step+1;m['training'].append(dict(step=step+1,length=n,batch=b,ids=ids,conditions=names,flow_loss=float(loss.detach()),gradient_norm=float(norm),adapter_gradient_norm=float(anorm),learning_rate_factor=factor,self_conditioned=info['self_conditioned'],noise_sha256=digest(info['noise']),time_sha256=digest(info['t']),drop_sha256=digest(info['dropped']),rng_sha256=digest(rng.get_state()),global_rng_sha256=digest(torch.cuda.get_rng_state())))
                    if (step+1)%20==0:atomic_json(a.output/'manifest.json',m);print('update',step+1,'loss',float(loss.detach()),flush=True)
                    del z,features,keep,mask,loss,info
                torch.cuda.synchronize();m['batches'].append(dict(begin=begin,end=end,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved()));m['frozen_final']=frozen_hash(model,frozen)
                if m['frozen_final']!=m['frozen_initial']:raise ValueError('Frozen weights changed')
                if not c['profile_only']:torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},fragment_adapter={k:v.cpu() for k,v in adapter_ema.items()},adapter_config=dict(output_width=model.d_model,hidden=recipe['adapter']['hidden'],variant='geometry' if geometry else 'token',n_layers=len(model.blocks),n_heads=model.n_heads,distance_precision=c.get('distance_precision','fp32')),arch=arch['architecture'],extra_arch=arch['extra_architecture'],model=arch['model'],experiment=c),a.output/f'ema_{end}.ckpt')
                evaluate(end)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
