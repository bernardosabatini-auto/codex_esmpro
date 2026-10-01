"""Fresh diffusion seeds with fixed versus independently sampled teacher trunks."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from benchmark_esmfold2 import backbone_indices
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json
from train_overfit import score_ensemble


def seed_for(seed,ident,stream):
    return int.from_bytes(hashlib.sha256(f'{seed}:{ident}:{stream}'.encode()).digest()[:8],'little')%(2**63-1)


def compare_backbones(left,right):
    if left.shape!=right.shape or left.ndim!=4 or left.shape[2:]!=(4,3):raise ValueError('control backbone shape mismatch')
    values=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(left,right)]
    result=dict(max_ca_rmsd=max(v['ca_rmsd'] for v in values),min_ca_lddt=min(v['ca_lddt'] for v in values))
    if result['max_ca_rmsd']>.01 or result['min_ca_lddt']<.999:raise ValueError('teacher replay/reproduction control failed: '+str(result))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['label_manifest'])
    if sha(path)!=c['label_manifest_sha256'] or sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('recurrence input changed')
    source=json.loads(path.read_text());labels=path.parent/'labels.h5';rows=source['config']['targets']
    if source['status']!='complete' or not source['training_gate_passed'] or sha(labels)!=c['labels_sha256']:raise ValueError('label audit changed')
    if len(rows)!=32 or {r['id'] for r in rows}!=set(c['teacher_seeds']) or (c['samples'],c['sample_batch'],c['steps'])!=(32,16,50):raise ValueError('unexpected recurrence protocol')
    folder=(a.source/'data/esmfold2_fast').resolve()
    for artifact in c['teacher_artifacts']:
        item=Path(artifact['path']);stat=item.stat()
        if item.parent.resolve()!=folder or (stat.st_size,stat.st_mtime_ns)!=(artifact['bytes'],artifact['mtime_ns']):raise ValueError('teacher changed since CPU hash verification')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],scores=[],batches=[],scope='Fresh teacher recurrence against the frozen training-only state atlas. Not biological populations or model accuracy.')
    atomic_json(a.output/'manifest.json',m)
    try:
        model,loading=load_fast_model(folder);m['teacher_adapter']=loading;sampler=model._sample_structure;telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(labels) as src,h5py.File(a.output/'predictions.h5','x') as out:
            for index,row in enumerate(rows):
                ident=row['id'];n=row['length'];g=src[ident]
                record=dict(state=json.loads(g.attrs['state_definition']),teacher_backbone=torch.from_numpy(g['teacher_backbone'][:]),reference_backbone=torch.from_numpy(g['reference_backbone'][:]))
                group=out.create_group(ident);group.attrs['sequence_sha256']=row['sequence_sha256']
                chunk_seeds=[seed_for(c['seed'],ident,f'diffusion:{offset}') for offset in (0,16)]
                new_seed=seed_for(c['seed'],ident,'new_trunk');old_seed=c['teacher_seeds'][ident]
                if len(set([old_seed,new_seed,*chunk_seeds]))!=4:raise ValueError('teacher random streams collided')
                for mode,fold_seed in [('fixed_trunk',old_seed),('new_trunk',new_seed)]:
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('teacher recurrence work cap')
                    name=f'collect::teacher_recurrence::{index}::{mode}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                    try:
                        torch.manual_seed(fold_seed);features=fast_features(row['sequence']);atoms=torch.as_tensor(backbone_indices(features,n),device='cuda');captured={}
                        def capture(**kwargs):
                            captured.update(kwargs=kwargs,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state())
                            return sampler(**kwargs)
                        model._sample_structure=capture
                        try:full=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=16)
                        finally:model._sample_structure=sampler
                        full_bb=full.sample_atom_coords[:,atoms,:].float().cpu().numpy();confidence=float(full.plddt.float().mean());del full
                        control=dict(target_id=ident,mode=mode,fold_seed=fold_seed,control_plddt=confidence)
                        if mode=='fixed_trunk':control['original']=compare_backbones(full_bb,record['teacher_backbone'].numpy())
                        torch.set_rng_state(captured['cpu_rng']);torch.cuda.set_rng_state(captured['cuda_rng'])
                        replay=sampler(**captured['kwargs'])[:,atoms,:].float().cpu().numpy();control['replay']=compare_backbones(full_bb,replay)
                        m['controls'].append(control);collected=[]
                        for seed in chunk_seeds:
                            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('teacher recurrence work cap')
                            torch.manual_seed(seed);kwargs=dict(captured['kwargs'],num_diffusion_samples=16,num_sampling_steps=50)
                            bb=sampler(**kwargs)[:,atoms,:].float()
                            if bb.shape!=(16,n,4,3) or not torch.isfinite(bb).all():raise ValueError('invalid fresh teacher backbone')
                            collected.append(bb)
                        combined=torch.cat(collected);score,_,_=score_ensemble(combined,record)
                        counts=np.bincount(record['state']['clusters']);assigned=np.asarray(score['assignments']);rare=np.flatnonzero(counts==1)
                        score.update(singleton_states=len(rare),singleton_hits=sum(bool((assigned==i).any()) for i in rare))
                        dst=group.create_group(mode);dst.create_dataset('backbone',data=combined.cpu().numpy());dst.create_dataset('chunk_seeds',data=np.asarray(chunk_seeds,dtype=np.int64))
                        m['scores'].append(dict(target_id=ident,mode=mode,**score));torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=32,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    out.flush();atomic_json(a.output/'manifest.json',m)
                    del captured,features,kwargs,bb,combined,collected,full_bb,replay
                print('teacher recurrence',index+1,'of32',flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
