"""Matched unconditional trajectory-compression training with raw evaluation."""
import argparse,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.generative import sample_unconditional
from latentfold.unconditional_training import freeze_unused_conditioning,unconditional_loss
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def frozen_hash(net,names):
    h=hashlib.sha256()
    for n,p in net.named_parameters():
        if n in names:h.update(n.encode());h.update(p.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','labels_manifest','pairs','checkpoint','decoder_checkpoint','selection','generation_manifest','initial_manifest','initial_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    recipe=json.loads(Path(c['protocol']).read_text());rows=json.loads(Path(c['selection']).read_text())['rows'];labels=json.loads(Path(c['labels_manifest']).read_text())
    if labels['status']!='complete' or labels['config']['protocol_sha256']!=c['protocol_sha256'] or labels['config']['checkpoint_sha256']!=c['checkpoint_sha256']:raise ValueError('Invalid source lineage')
    if c['arm'] not in recipe['arms'] or c['seed']!=recipe['training_seed'] or c['batches']!=recipe['batches'] or c['schedule_updates']!=1000 or c['updates']!=(40 if c['profile_only'] else 1000):raise ValueError('Wrong training recipe')
    for key in ('learning_rate','warmup_updates','ema_decay'):
        if c[key]!=recipe[key]:raise ValueError('Changed training parameter '+key)
    if c['evaluation_steps']!=([40] if c['profile_only'] else [500,1000]):raise ValueError('Changed evaluation schedule')
    if not c['profile_only']:
        if sha(c['profile_report'])!=c['profile_report_sha256'] or not json.loads(Path(c['profile_report']).read_text())['profile_qualified']:raise ValueError('Profile not qualified')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,updates=0,training=[],batches=[],evaluations=[],initial_controls=[],sampling_controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        data={}
        with h5py.File(c['pairs']) as f:
            if set(f)!=set(map(str,recipe['lengths'])):raise ValueError('Incomplete labels')
            for n in recipe['lengths']:data[n]={key:torch.from_numpy(f[str(n)][key][:]) for key in ('noise','endpoint')}
        model,arch=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True;frozen=freeze_unused_conditioning(model);m['frozen_names']=frozen;m['frozen_initial']=frozen_hash(model,frozen)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();ema={k:v.detach().clone() for k,v in model.state_dict().items()};parameters=[p for p in model.parameters() if p.requires_grad];m['trainable_parameters']=sum(p.numel() for p in parameters)
        torch.manual_seed(c['seed']);optimizer=torch.optim.AdamW(parameters,lr=c['learning_rate'],betas=(.9,.95),weight_decay=.01,foreach=False);order=np.random.default_rng(c['seed']);rng=torch.Generator(device='cuda').manual_seed(c['seed']);queues={n:[] for n in recipe['lengths']};telemetry=Telemetry(a.output,True)
        def evaluate(step):
            raw={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};model.load_state_dict(ema);model.eval();tick=time.monotonic();scores=[]
            with torch.no_grad(),inference_precision('fp32'),h5py.File(c['initial_predictions']) as initial,h5py.File(a.output/f'evaluation_{step}.h5','x') as f:
                for row in rows:
                    ident=row['target_id'];n=row['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');esm=torch.zeros(4,n,2560,device='cuda');noise=torch.cat([target_noise([ident],[n],8,seed=c['generation_seed'],sample_index=k,stream='flow:0',device='cuda') for k in range(4)]);dn=torch.cat([target_noise([ident],[4*n],3,seed=c['generation_seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                    z=sample_unconditional(model,esm,mask,noise=noise,steps=10);_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();geom=backbone_geometry(bb);g=f.create_group(ident);g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=z.cpu().numpy())
                    if step==0:
                        expected=initial['original10/unconditional/'+ident+'/backbone'][:];valid=backbone_geometry(expected)['coarse_valid']
                        for k in range(4):
                            check=dict(target_id=ident,slot=k,validity_identical=bool(valid[k]==geom['coarse_valid'][k]),**ca_metrics(bb[k,:,1],expected[k,:,1]));m['initial_controls'].append(check);atomic_json(a.output/'manifest.json',m)
                            if check['ca_rmsd']>.2 or check['ca_lddt']<.99 or not check['validity_identical']:raise ValueError('Initial prediction identity failed')
                    if ident in c['control_ids']:
                        generic=sample(model,esm[:1],mask[:1],SampleConfig(steps=10,guidance=0),noise=noise[:1]);alone=sample_unconditional(model,esm[:1],mask[:1],noise=noise[:1],steps=10);metric=dict(step=step,target_id=ident,latent_max_abs=float((generic-alone).abs().max()));m['sampling_controls'].append(metric);atomic_json(a.output/'manifest.json',m)
                        if metric['latent_max_abs']>1e-5:raise ValueError('Trained null sampling parity failed')
                    scores.extend(dict(target_id=ident,family=row['family'],slot=k,coarse_valid=int(geom['coarse_valid'][k])) for k in range(4))
                f.flush()
            m['evaluations'].append(dict(step=step,scores=scores,seconds=time.monotonic()-tick));model.load_state_dict(raw);model.train();del raw;atomic_json(a.output/'manifest.json',m)
        evaluate(0)
        with inference_precision('fp32'):
            for begin,end in zip([0]+c['evaluation_steps'][:-1],c['evaluation_steps']):
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                for step in range(begin,end):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Unconditional training cap')
                    n=recipe['lengths'][step%len(recipe['lengths'])];b=c['batches'][str(n)]
                    if len(queues[n])<b:queues[n]=order.permutation(recipe['labels_per_length']).tolist()
                    indices=queues[n][:b];del queues[n][:b];z=data[n]['endpoint'][indices].cuda();noise=data[n]['noise'][indices].cuda();mask=torch.ones(b,n,dtype=torch.bool,device='cuda')
                    lr=c['learning_rate']*min((step+1)/c['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*step/(c['schedule_updates']-1))));optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
                    loss,info=unconditional_loss(model,z,mask,recorded_noise=noise,paired=c['arm']=='paired',generator=rng);loss.backward();norm=torch.nn.utils.clip_grad_norm_(parameters,1.,error_if_nonfinite=True)
                    if not torch.isfinite(loss) or norm<=0:raise FloatingPointError('Invalid loss or gradient')
                    optimizer.step()
                    with torch.no_grad():
                        values=model.state_dict();keys=[k for k in ema if ema[k].is_floating_point()];torch._foreach_lerp_([ema[k] for k in keys],[values[k] for k in keys],1-c['ema_decay'])
                    m['updates']=step+1;m['training'].append(dict(step=step+1,length=n,batch=b,indices=indices,flow_loss=float(loss.detach()),gradient_norm=float(norm),learning_rate=lr,self_conditioned=info['self_conditioned'],time_sha256=hashlib.sha256(info['t'].cpu().numpy().tobytes()).hexdigest(),rng_sha256=hashlib.sha256(rng.get_state().cpu().numpy().tobytes()).hexdigest(),global_rng_sha256=hashlib.sha256(torch.cuda.get_rng_state().cpu().numpy().tobytes()).hexdigest()))
                    if (step+1)%20==0:atomic_json(a.output/'manifest.json',m);print('update',step+1,'loss',float(loss.detach()),flush=True)
                    del z,noise,mask,loss
                torch.cuda.synchronize();m['batches'].append(dict(begin=begin,end=end,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved()));m['frozen_final']=frozen_hash(model,frozen)
                if m['frozen_final']!=m['frozen_initial']:raise ValueError('Unused conditioning weights changed')
                if not c['profile_only']:torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},arch=arch['architecture'],extra_arch=arch['extra_architecture'],model=arch['model'],experiment=c),a.output/f'ema_{end}.ckpt')
                evaluate(end)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
