"""Profile bounded confidence on H100 against frozen full-confidence labels."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from benchmark_esmfold2 import backbone_indices
from confidence_chunks import chunk_confidence
from expansion_data import eligibility
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','base_profile'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    for path,expected in {(r['labels'],r['labels_sha256']) for r in c['targets']}:
        if sha(path)!=expected:raise ValueError('changed saved teacher labels')
    if len(c['targets'])!=8 or len({r['id'] for r in c['targets']})!=8:raise ValueError('eight distinct frozen controls required')
    for artifact in c['teacher_artifacts']:
        s=Path(artifact['path']).stat()
        if s.st_size!=artifact['bytes'] or s.st_mtime_ns!=artifact['mtime_ns']:raise ValueError('teacher artifact changed')
    a.output.mkdir(parents=True,exist_ok=False);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,records=[],batches=[]);atomic_json(a.output/'manifest.json',m)
    try:
        m['gpu']=torch.cuda.get_device_name(0)
        if 'H100' not in m['gpu']:raise ValueError('H100 profile hardware required')
        model,adapter=load_fast_model(a.source/'data/esmfold2_fast');m['teacher_adapter']=adapter;telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),chunk_confidence(model,4):
            for index,r in enumerate(sorted(c['targets'],key=lambda r:-r['length'])):
                if time.monotonic()-start>480:raise TimeoutError('confidence profile work budget')
                with h5py.File(r['labels']) as h:reference=h[r['id']]['teacher_backbone'][:];confidence=h[r['id']]['teacher_plddt'][:];valid=h[r['id']]['coarse_valid'][:].astype(bool)
                seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{r['id']}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed)
                name=f'collect::confidence_chunks::{index}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                try:
                    features=fast_features(r['sequence']);indices=backbone_indices(features,r['length']);prediction=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=16)
                    bb=prediction.sample_atom_coords[:,torch.as_tensor(indices,device='cuda'),:].float().cpu().numpy();plddt=prediction.plddt.float().cpu().numpy();del prediction,features
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                m['batches'].append(dict(nvtx_range=name,length=r['length'],batch=16,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated()))
                actual_valid=backbone_geometry(bb)['coarse_valid'];expected_state,expected_reason=eligibility(reference,valid,confidence);state,reason=eligibility(bb,actual_valid,plddt)
                states_equal=(state is None and expected_state is None) or (state is not None and expected_state is not None and all(state[key]==expected_state[key] for key in ('i','j','teacher_indices','clusters','states','core_residues')))
                scores=[ca_metrics(bb[k,:,1],reference[k,:,1]) for k in range(16)];delta=plddt-confidence
                row=dict(id=r['id'],bucket=r['bucket'],max_ca_rmsd=max(s['ca_rmsd'] for s in scores),min_ca_lddt=min(s['ca_lddt'] for s in scores),confidence_rmse=float(np.sqrt(np.mean(delta**2))),confidence_max_abs=float(np.abs(delta).max()),validity_exact=bool(np.array_equal(valid,actual_valid)),confident_mask_exact=bool(np.array_equal(confidence.mean(0)>=.7,plddt.mean(0)>=.7)),eligibility_exact=reason==expected_reason,states_exact=states_equal)
                row['passed']=bool(row['max_ca_rmsd']<=.2 and row['min_ca_lddt']>=.99 and row['confidence_rmse']<=1e-4 and row['confidence_max_abs']<=1e-3 and all(row[k] for k in ('validity_exact','confident_mask_exact','eligibility_exact','states_exact')))
                m['records'].append(row);atomic_json(a.output/'manifest.json',m);print(r['id'],row['passed'],flush=True)
        m['qualified']=all(r['passed'] for r in m['records']) and max(b['peak_reserved_bytes'] for b in m['batches'])<=64*1024**3;m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
