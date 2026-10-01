"""Eight stochastic teacher trunks times four diffusion draws; cache only ESMC."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from transformers.models.esmfold2.modeling_esmfold2 import EsmFold2AtomInputs
from latentfold.teacher import fast_features,load_fast_model
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from benchmark_esmfold2 import backbone_indices
from predict import file_identity
from profile_gpu import Telemetry,atomic_json


def trunk_inputs(features,hidden):
    values=dict(features);values.pop('distogram_atom_idx');values['input_ids']=None;values['lm_hidden_states']=hidden
    values['atom_inputs']=EsmFold2AtomInputs(**{k:values.pop(k) for k in ('ref_pos','ref_charge','atom_attention_mask','ref_element','ref_atom_name_chars','ref_space_uid','atom_to_token')})
    return values


def sample_kwargs(trunk,mask,count):
    return dict(pair_trunk=trunk.pair_states,single_inputs=trunk.single_inputs,relative_position_encoding=trunk.relative_position_encoding,atom_inputs=trunk.atom_inputs,attention_mask=mask,num_diffusion_samples=count,num_sampling_steps=50)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['panel'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('changed panel')
    allrows={r['query_id']:r for r in json.loads(path.read_text())['development']};rows=[allrows[k] for k in c['target_ids']]
    if c['trunk_replicates']!=8 or c['sample_batch']!=4 or c['samples']!=32 or c['steps']!=[50]:raise ValueError('unexpected factorial protocol')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',config=c,batches=[],controls=[],targets=[],precision='strict FP32',timing_scope='ESMC cached once per target; production includes stochastic trunk and structure sampling, excludes confidence. Numerical controls include full fold.');telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        folder=a.source/'data/esmfold2_fast';m['artifacts']=[file_identity(p,hash_contents=True) for p in sorted(folder.glob('*')) if p.suffix in ('.json','.safetensors')]
        model,loading=load_fast_model(folder);m['teacher_adapter']=loading;telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as output:
            for index,row in enumerate(rows):
                ident=row['query_id'];n=row['length'];features=fast_features(row['sequence']);atom_index=backbone_indices(features,n);cache={};compute=model._compute_lm_hidden_states
                def save_hidden(*args,**kwargs):
                    cache['hidden']=compute(*args,**kwargs);return cache['hidden']
                seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:control".encode()).digest()[:8],'little')%(2**63-1)
                torch.manual_seed(seed);model._compute_lm_hidden_states=save_hidden
                try:full=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=4)
                finally:model._compute_lm_hidden_states=compute
                expected=full.sample_atom_coords.float().cpu().numpy()[:,atom_index,:];del full
                # Same initial RNG state: caching ESMC must not remove random draws.
                torch.manual_seed(seed);trunk=model(**trunk_inputs(features,cache['hidden']),num_loops=3)
                actual=model._sample_structure(**sample_kwargs(trunk,features['attention_mask'],4)).float().cpu().numpy()[:,atom_index,:];del trunk
                metrics=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(expected,actual)];m['controls'].append(dict(target_id=ident,metrics=metrics))
                if any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in metrics):raise ValueError('cached-ESMC full-trunk parity failed')
                samples=[];seeds=[]
                for k in range(8):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('work cap')
                    trunk_seed=seed if k==0 else int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:trunk:{k}".encode()).digest()[:8],'little')%(2**63-1)
                    diffusion_seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:diffusion:{k}".encode()).digest()[:8],'little')%(2**63-1)
                    name=f'collect::teacher_trunks::{index}::{k}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                    try:
                        torch.manual_seed(trunk_seed);trunk=model(**trunk_inputs(features,cache['hidden']),num_loops=3)
                        torch.manual_seed(diffusion_seed);bb=model._sample_structure(**sample_kwargs(trunk,features['attention_mask'],4)).float().cpu().numpy()[:,atom_index,:];del trunk
                        torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all():raise ValueError('invalid teacher sample')
                    samples.append(bb);seeds.append((trunk_seed,diffusion_seed));m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=4,steps=50,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                g=output.create_group(ident).create_group('steps50');g.create_dataset('backbone',data=np.concatenate(samples));g.create_dataset('trunk_diffusion_seeds',data=np.asarray(seeds,dtype=np.int64))
                output.flush();m['targets'].append(dict(id=ident,length=n));atomic_json(a.output/'manifest.json',m);print('teacher trunk factorial',index+1,'of',len(rows),flush=True);del cache,features
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
