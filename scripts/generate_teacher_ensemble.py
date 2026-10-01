"""Validate trunk reuse and measure ESMFold2 seed/step diversity on development."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from benchmark_esmfold2 import backbone_indices
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from predict import file_identity
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['panel'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('changed panel')
    allrows={r['query_id']:r for r in json.loads(path.read_text())['development']};rows=[allrows[k] for k in c['target_ids']]
    batch=c['sample_batch']
    if len(rows)!=len(set(c['target_ids'])) or batch not in (8,16) or c['samples']!=32:raise ValueError('unexpected pilot sampling protocol')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',config=c,batches=[],controls=[],targets=[],precision='strict FP32',timing_scope='Structure-only sampling reuses trunk, excludes confidence head. Full fold controls include confidence. Do not compare structure-only timing against full-fold timing as an end-to-end speedup.');telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        folder=a.source/'data/esmfold2_fast';m['artifacts']=[file_identity(p,hash_contents=True) for p in sorted(folder.glob('*')) if p.suffix in ('.json','.safetensors')]
        model,loading=load_fast_model(folder);m['teacher_adapter']=loading;atomic_json(a.output/'manifest.json',m);telemetry=Telemetry(a.output,True)
        sampler=model._sample_structure
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as output:
            for i,row in enumerate(rows):
                ident=row['query_id'];n=row['length'];features=fast_features(row['sequence'],device='cuda');atom_index=backbone_indices(features,n);captured={}
                def capture(**kwargs):
                    captured.update(kwargs=kwargs,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state())
                    return sampler(**kwargs)
                seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:control".encode()).digest()[:8],'little')%(2**63-1)
                torch.manual_seed(seed);model._sample_structure=capture;torch.cuda.synchronize();tick=time.monotonic()
                try:full=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=batch)
                finally:model._sample_structure=sampler
                ref=full.sample_atom_coords.float().cpu().numpy()[:,atom_index,:];del full;torch.cuda.synchronize();full_seconds=time.monotonic()-tick
                torch.set_rng_state(captured['cpu_rng']);torch.cuda.set_rng_state(captured['cuda_rng'])
                reused=sampler(**captured['kwargs']).float().cpu().numpy()[:,atom_index,:]
                controls=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(ref,reused)]
                m['controls'].append(dict(target_id=ident,full_fold_seconds=full_seconds,metrics=controls))
                if any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in controls):raise ValueError('trunk-reuse control failed')
                target=output.create_group(ident);target.attrs['sequence_sha256']=hashlib.sha256(row['sequence'].encode()).hexdigest()
                for steps in c['steps']:
                    sg=target.create_group(f'steps{steps}');samples=[];seeds=[]
                    for offset in range(0,32,batch):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('experiment work cap')
                        # Same chunk seed across integration-step settings; trajectories still differ.
                        seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:chunk:{offset}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed)
                        kwargs=dict(captured['kwargs'],num_diffusion_samples=batch,num_sampling_steps=steps)
                        name=f'collect::teacher::{i}::{steps}::{offset}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:
                            bb=sampler(**kwargs).float().cpu().numpy()[:,atom_index,:];torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        if bb.shape!=(batch,n,4,3) or not np.isfinite(bb).all():raise ValueError('invalid teacher backbone')
                        samples.append(bb);seeds.append(seed);m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=batch,steps=steps,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    sg.create_dataset('backbone',data=np.concatenate(samples));sg.create_dataset('chunk_seeds',data=np.asarray(seeds,dtype=np.int64))
                m['targets'].append(dict(id=ident,length=n));output.flush();atomic_json(a.output/'manifest.json',m);print('teacher ensemble',i+1,'of',len(rows),flush=True)
                del captured,features,kwargs
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
