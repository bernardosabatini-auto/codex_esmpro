"""Matched continued-training pilot, followed by full-sampling development scoring."""
import argparse,gc,hashlib,json,math,os,sys,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.data import collate
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig
from latentfold.training import objective,controlled_backward
from latentfold.precision import inference_precision
from latentfold.quality import confidence_weights
from profile_gpu import atomic_json,Telemetry


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def train(config,task,out):
    source=Path(config['source']);start=time.monotonic()
    manifest_path=Path(config['training_manifest']);holdout=Path(config['holdout_manifest'])
    if sha(manifest_path)!=config['training_manifest_sha256'] or sha(holdout)!=config['holdout_manifest_sha256']:
        raise ValueError('training or locked-test provenance changed')
    data=json.loads(manifest_path.read_text())
    if data['status']!='complete':raise ValueError('training data incomplete')
    locked=json.loads(holdout.read_text())
    if locked.get('status')!='selection_protocol_locked' and len(locked.get('targets',[]))<32:
        raise ValueError('neither test-selection protocol nor final manifest was locked')
    report=dict(status='running',task=task,config=config,rows=[],steps=0,batches=[],job_id=os.environ.get('SLURM_JOB_ID'))
    atomic_json(out/'training.json',report)
    torch.manual_seed(task['seed']);torch.set_num_threads(4);torch.cuda.set_device(0)
    torch.cuda.set_per_process_memory_fraction(.85);torch.set_float32_matmul_precision('highest')
    torch.backends.cudnn.allow_tf32=False
    records={};buckets={int(k):[] for k in config['batches']}
    weights=None
    if config.get('confidence_weights'):
        wp=Path(config['confidence_weights'])
        if sha(wp)!=config['confidence_weights_sha256']:raise ValueError('confidence weights changed')
        weights=json.loads(wp.read_text())
        if weights['training_manifest_sha256']!=config['training_manifest_sha256']:raise ValueError('confidence data differ')
        if task['arm']!='confidence':raise ValueError('confidence weighting must be its own ablation arm')
    with h5py.File(data['dataset'],'r') as h:
        if set(h['train'])!={r['id'] for r in data['records']}:raise ValueError('training coverage changed')
        for meta in data['records']:
            name=meta['id'];g=h['train'][name]
            record=dict(id=name,sequence=str(g.attrs['sequence']),**{k:torch.from_numpy(g[src][:]) for k,src in [('esm','esm2_emb'),('z','z'),('ca','ca_coords')]})
            if 'adjacent' in g:record['adjacent']=torch.from_numpy(g['adjacent'][:])
            elif task['arm']=='geometry':raise ValueError('geometry training requires verified residue correspondence')
            else:record['adjacent']=torch.zeros(len(record['sequence'])-1,dtype=torch.bool)
            if hashlib.sha256(record['sequence'].encode()).hexdigest()!=meta['sequence_sha256']:raise ValueError('training sequence mismatch')
            if weights is not None:
                confidence=g['plddt'][:].astype(np.float32)
                if hashlib.sha256(confidence.tobytes()).hexdigest()!=weights['records'][name]['confidence_array_sha256']:
                    raise ValueError('training confidence changed')
                record['residue_weights']=confidence_weights(torch.from_numpy(confidence),weights['buckets'][str(meta['bucket'])]['mean_raw_weight'])
            records[name]=record;buckets[meta['bucket']].append(name)
    initial=source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt'
    decoder_path=source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt'
    if sha(initial)!=config['initial_checkpoint_sha256'] or sha(decoder_path)!=config['decoder_checkpoint_sha256']:
        raise ValueError('source checkpoint changed since the strict FP32 baseline')
    model,arch=load_legacy(initial,trusted_pickle=True)
    model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
    decoder=load_proteinae(source/'ProteinAE_v1',source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
    if config.get('gradient_controls'):
        from check_training_precision import check
        report['gradient_controls']=check(model,decoder,records,buckets,flow_config=FlowConfig(**config.get('flow_config',{})),weighted=False)
        atomic_json(out/'training.json',report)
        if not all(r['passed'] for r in report['gradient_controls']):
            report.update(status='failed',error='FP16 actual parameter-gradient controls failed')
            atomic_json(out/'training.json',report);raise ValueError(report['error'])
    if weights is not None:
        try:
            from check_training_precision import check
            report['weighted_gradient_controls']=check(model,decoder,records,buckets)
            if not all(r['passed'] for r in report['weighted_gradient_controls']):
                raise ValueError('confidence-weighted FP16 gradient controls failed')
            atomic_json(out/'training.json',report)
        except BaseException as error:
            report.update(status='failed',error=f'{type(error).__name__}: {error}')
            atomic_json(out/'training.json',report);raise
    # Keep previous pilots reproducible while making recovery ablations explicit.
    optimizer=torch.optim.AdamW(model.parameters(),lr=config['learning_rate'],weight_decay=.01,
                               betas=tuple(config.get('optimizer_betas',(.9,.999))),foreach=False)
    ema={k:v.detach().clone() for k,v in model.state_dict().items()}
    flow_config=FlowConfig(**config.get('flow_config',{}));flow_rng=torch.Generator(device='cuda').manual_seed(task['seed'])
    order_rng=np.random.default_rng(task['seed']);queues={k:[] for k in buckets}
    weight=config['geometry_weight'] if task['arm']=='geometry' else 0.
    telemetry=Telemetry(out,True);range_active=False
    try:
        torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();train_start=time.monotonic()
        torch.cuda.nvtx.range_push('train::updates');range_active=True
        for step in range(config['updates']):
            if time.monotonic()-start>60*config['training_minutes']:raise TimeoutError('training walltime guard')
            bucket=sorted(buckets)[step%len(buckets)];count=config['batches'][str(bucket)]
            if len(queues[bucket])<count:
                queues[bucket]=order_rng.permutation(buckets[bucket]).tolist()
            ids=queues[bucket][:count];del queues[bucket][:count]
            chosen=[records[name] for name in ids];batch=collate(chosen)
            if weights is not None:
                batch['residue_weights']=torch.zeros(count,batch['mask'].shape[1])
                for i,r in enumerate(chosen):batch['residue_weights'][i,:len(r['residue_weights'])]=r['residue_weights']
            batch['adjacent']=torch.zeros(count,batch['mask'].shape[1]-1,dtype=torch.bool)
            for i,r in enumerate(chosen):batch['adjacent'][i,:len(r['adjacent'])]=r['adjacent']
            padding=bucket-batch['mask'].shape[1]
            for k in ('z','ca','esm'):batch[k]=F.pad(batch[k],(0,0,0,padding))
            for k in ('mask','adjacent'):batch[k]=F.pad(batch[k],(0,padding))
            if weights is not None:batch['residue_weights']=F.pad(batch['residue_weights'],(0,padding))
            batch={k:v.pin_memory().to('cuda',non_blocking=True) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
            progress=step/max(config['updates']-1,1)
            lr=config['learning_rate']*min((step+1)/config['warmup_updates'],1)*(.3+.7*.5*(1+math.cos(math.pi*progress)))
            optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
            with inference_precision('fp16'):
                flow,geometry,stats=objective(model,decoder,batch,flow_config,generator=flow_rng,
                    geometry_weight=weight,geometry_seed=task['seed']+100000,step=step,
                    max_geometry=4,return_parts=True)
            stats.update(controlled_backward(model,flow,geometry,weight=weight,
                max_ratio=config['aux_gradient_cap'],loss_scale=128.))
            norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
            optimizer.step()
            with torch.no_grad():
                values=model.state_dict();keys=[k for k,v in ema.items() if v.is_floating_point()]
                torch._foreach_lerp_([ema[k] for k in keys],[values[k] for k in keys],1-config['ema_decay'])
                for key,value in ema.items():
                    if not value.is_floating_point():value.copy_(values[key])
            report['steps']=step+1
            if step%20==0 or step+1==config['updates']:
                torch.cuda.synchronize()
                row=dict(step=step+1,bucket=bucket,batch=count,learning_rate=lr,
                         flow_rng_sha256=hashlib.sha256(flow_rng.get_state().numpy().tobytes()).hexdigest(),
                         input_ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
                         elapsed_training_seconds=time.monotonic()-train_start,gradient_norm=float(norm),**stats)
                report['rows'].append(row);atomic_json(out/'training.json',report);print(json.dumps(row),flush=True)
            del flow,geometry,batch
        torch.cuda.synchronize();torch.cuda.nvtx.range_pop();range_active=False
        report['batches']=[dict(nvtx_range='train::updates')]
        report.update(training_seconds=time.monotonic()-train_start,
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved())
        checkpoint=out/'final_ema.ckpt'
        torch.save(dict(ema={k:v.cpu() for k,v in ema.items()},arch=arch['architecture'],
                        extra_arch=arch['extra_architecture'],model=arch['model'],pilot_config=config,task=task),checkpoint)
        report.update(status='complete',checkpoint=str(checkpoint.resolve()),checkpoint_sha256=sha(checkpoint))
    except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if range_active:torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
        telemetry.close();report['elapsed_seconds']=time.monotonic()-start;atomic_json(out/'training.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    p.add_argument('--task',type=int,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();config=json.loads(a.config.read_text());task=config['tasks'][a.task]
    config.update(task.get('overrides',{}))
    a.output.mkdir(parents=True,exist_ok=False)
    report=train(config,task,a.output)
    gc.collect();torch.cuda.empty_cache()
    evaluation=json.loads(Path(config['evaluation_template']).read_text())
    evaluation.update(flow_steps=[25],guidance=[2],samples=3,flow_precision='fp32',decoder_precision='fp32',internal_minutes=35,
        target_manifest=str((Path(config['evaluation_template']).parent/evaluation['target_manifest']).resolve()))
    evaluation['models']={'pair':dict(checkpoint=report['checkpoint'],batches=config['evaluation_batches'])}
    path=a.output/'evaluation_config.json';atomic_json(path,evaluation)
    import collect_comparison
    sys.argv=['collect_comparison.py','--source',config['source'],'--config',str(path),'--model','pair',
        '--output',str(a.output/'evaluation'),'--nsys-metrics','--allow-gpu','--score-workers','1',
        '--usalign',str(Path(__file__).resolve().parents[1]/'runs/tools/USalign/USalign')]
    collect_comparison.main()

if __name__=='__main__':main()
