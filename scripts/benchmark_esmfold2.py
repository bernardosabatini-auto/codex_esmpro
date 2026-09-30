"""External sequence-to-structure benchmark with fixed correspondence and full coverage."""
import argparse,hashlib,json,multiprocessing,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import h5py,numpy as np,torch
from transformers.models.esmfold2.modeling_esmfold2 import EsmFold2Model
from transformers.models.esmfold2.protein_utils import prepare_protein_features
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from profile_gpu import Telemetry,atomic_json
from score_comparison import score_batch,write_scores


def backbone_indices(features,length):
    names=[''.join(chr(int(x)+32) if x else ' ' for x in row).strip() for row in features['ref_atom_name_chars'][0].cpu().numpy()]
    tokens=features['atom_to_token'][0].cpu().numpy();valid=features['atom_attention_mask'][0].cpu().numpy()
    result=[]
    for residue in range(length):
        atoms={name:[] for name in ('N','CA','C','O')}
        for i in np.where(valid & (tokens==residue))[0]:
            if names[i] in atoms:atoms[names[i]].append(i)
        if any(len(v)!=1 for v in atoms.values()):raise ValueError('ambiguous backbone atom correspondence')
        result.append([atoms[name][0] for name in ('N','CA','C','O')])
    return np.array(result)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--ids',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--usalign',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
 ids=a.ids.read_text().splitlines()
 if len(ids)!=626 or len(ids)!=len(set(ids)):raise ValueError('expected exactly 626 unique development targets')
 started=time.monotonic();report=dict(status='running',model='ESMFold2-Fast',target_ids=ids,samples=3,num_loops=3,num_sampling_steps=50,
   precision='strict FP32',timing_scope='full sequence to all-atom structure; includes conditioner and confidence head; three parallel samples per target',
   batches=[],controls=[],completed_predictions=0,model_directory=str(a.source/'data/esmfold2_fast'))
 atomic_json(a.output/'manifest.json',report);telemetry=None;scorers=None;futures=[]
 try:
  with h5py.File(a.source/'data/phase1_dataset/dataset_exp_val_esmc.h5','r') as h:
   records=[dict(id=name,sequence=str(h['val'][name].attrs['sequence']),ca=h['val'][name]['ca_coords'][:]) for name in ids]
  artifacts=[]
  for path in sorted((a.source/'data/esmfold2_fast').glob('*')):
   if path.is_file() and path.suffix in ('.safetensors','.bin','.json'):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
     for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    artifacts.append(dict(name=path.name,bytes=path.stat().st_size,sha256=digest.hexdigest()))
  report['model_artifacts']=artifacts
  model=EsmFold2Model.from_pretrained(a.source/'data/esmfold2_fast',dtype=torch.float32,local_files_only=True).eval().cuda().requires_grad_(False)
  report['parameter_dtypes']=sorted({str(p.dtype) for p in model.parameters()})
  if report['parameter_dtypes']!=['torch.float32']:raise ValueError('model did not load entirely in FP32')
  report['parameters']=sum(p.numel() for p in model.parameters());report['gpu']=torch.cuda.get_device_name(0)
  report['model_config_sha256']=hashlib.sha256((a.source/'data/esmfold2_fast/config.json').read_bytes()).hexdigest()
  telemetry=Telemetry(a.output,True);scorers=ProcessPoolExecutor(max_workers=1,mp_context=multiprocessing.get_context('spawn'))
  with inference_precision('fp32'),torch.no_grad(),h5py.File(a.output/'predictions.h5','x') as predictions:
   # Repeat the exact sampled calculation, no implicit best-of-three rendering.
   control_records=[min(records,key=lambda r:len(r['sequence'])),max(records,key=lambda r:len(r['sequence']))]
   for r in control_records:
    features=prepare_protein_features(r['sequence'],device='cuda');index=backbone_indices(features,len(r['sequence']));coordinates=[]
    for repeat in range(2):
     torch.manual_seed(71);output=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=3)
     coordinates.append(output.sample_atom_coords.float().cpu().numpy()[:,index, :][:,:,1,:]);del output
    metrics=[ca_metrics(x,y) for x,y in zip(*coordinates)]
    if any(m['ca_rmsd']>.01 or m['ca_lddt']<.999 for m in metrics):raise ValueError('external model repeatability control failed')
    report['controls'].append(dict(id=r['id'],metrics=metrics))
   for i,r in enumerate(records):
    if time.monotonic()-started>2100:raise TimeoutError('35-minute work cap; no incomplete benchmark claim')
    seed=int.from_bytes(hashlib.sha256(('esmfold2:'+r['id']).encode()).digest()[:8],'little')%(2**63-1)
    torch.manual_seed(seed);torch.cuda.synchronize();begin=time.monotonic();nvtx=f'collect::esmfold2::{i}'
    torch.cuda.nvtx.range_push(nvtx)
    features=prepare_protein_features(r['sequence'],device='cuda');index=backbone_indices(features,len(r['sequence']))
    output=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=3)
    backbone=output.sample_atom_coords.float().cpu().numpy()[:,index,:]
    if backbone.shape!=(3,len(r['sequence']),4,3) or not np.isfinite(backbone).all():raise ValueError('invalid structure output')
    torch.cuda.synchronize();seconds=time.monotonic()-begin;torch.cuda.nvtx.range_pop()
    group=predictions.create_group(r['id']);group.attrs['sequence_sha256']=hashlib.sha256(r['sequence'].encode()).hexdigest();group.create_dataset('backbone',data=backbone)
    futures.append(scorers.submit(score_batch,[('esmfold2_steps50_loops3',r['id'],k,backbone[k,:,1],r['ca'],backbone[k],str(a.usalign.resolve())) for k in range(3)]))
    report['completed_predictions']+=3;report['batches'].append(dict(nvtx_range=nvtx,seconds=seconds,proteins=1,predictions=3))
    del output,features
    if i%20==0 or i==625:
     report.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved())
     atomic_json(a.output/'manifest.json',report);print('completed',i+1,'/',len(records),'seconds',time.monotonic()-started,flush=True)
  rows=[row for future in futures for row in future.result()]
  expected={(name,k) for name in ids for k in range(3)}
  keys=[(r['target_id'],r['sample']) for r in rows]
  if len(keys)!=len(expected) or set(keys)!=expected:raise ValueError('incomplete or duplicate scoring')
  write_scores(a.output,report,rows,time.monotonic()-started,str(a.usalign.resolve()),'overlapped CPU scoring')
  report['status']='complete'
 except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:
  if scorers:scorers.shutdown(wait=True,cancel_futures=True)
  if telemetry:telemetry.close()
  report['elapsed_seconds']=time.monotonic()-started;atomic_json(a.output/'manifest.json',report)

if __name__=='__main__':main()
