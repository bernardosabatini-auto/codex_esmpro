"""Sequence-to-backbone throughput, including fresh final-layer ESMC extraction."""
import argparse,json,multiprocessing,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.embedding import FinalESMC
from latentfold.batching import prediction_batch,requests_by_bucket
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.data import read_record
from latentfold.flow import SampleConfig
from latentfold.metrics import ca_metrics
from collect_comparison import infer,write_batch
from predict import file_identity
from profile_gpu import atomic_json,Telemetry
from score_comparison import score_batch,write_scores
from online_analysis import sampling_parameters


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
 p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--usalign',type=Path,required=True);a=p.parse_args()
 config=json.loads(a.config.read_text());ids=Path(config['target_manifest']).read_text().splitlines()
 steps,guidance,setting=sampling_parameters(config)
 if len(ids)!=626 or len(set(ids))!=626:raise ValueError('expected exact 626-target benchmark')
 a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0)
 torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic()
 config['target_ids']=ids
 manifest=dict(status='running',model='pair_online_final_esmc',config=config,source=str(a.source),completed_predictions=0,batches=[],controls=[],
    timing_scope='batched sequences to three backbone predictions, including tokenization, ESMC, head, decoder and coordinate transfer; excludes model loading, validation, scoring and artifact writes',
    precision=dict(embedding=config.get('embedding_precision','bf16'),head=config.get('flow_precision','fp16_mlp'),decoder='fp32'),samples=3)
 atomic_json(a.output/'manifest.json',manifest);telemetry=None;scorers=None
 try:
  path=a.source/'data/phase1_dataset/dataset_exp_val_esmc.h5';records=[read_record(path,'val',n,embedding_dim=2560) for n in ids]
  manifest['dataset']=file_identity(path)
  ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';manifest['checkpoint']=file_identity(ckpt,hash_contents=True)
  model,arch=load_legacy(ckpt,trusted_pickle=True);model.cuda().eval().requires_grad_(False)
  ae=a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt';manifest['decoder_checkpoint']=file_identity(ae,hash_contents=True)
  decoder=load_proteinae(a.source/'ProteinAE_v1',ae).cuda();embedding=FinalESMC(a.source/'data/esmc6b',precision=config.get('embedding_precision','bf16'))
  manifest['embedding_artifacts']=[file_identity(p,hash_contents=True) for p in sorted((a.source/'data/esmc6b').glob('*')) if p.is_file() and p.suffix in ('.json','.safetensors')]
  manifest['resident_parameters']=sum(p.numel() for m in (model,decoder,embedding.model) for p in m.parameters())
  cfg=SampleConfig(steps=steps,guidance=guidance);batches={int(k):v for k,v in config['batches'].items()};buckets=requests_by_bucket(records,batches,3)
  options=dict(flow_precision=config.get('flow_precision','fp16_mlp'),decoder_precision='fp32')
  def tensors(requests,length):
   unique={r['id']:r for r,_ in requests};ordered=list(unique);index={name:i for i,name in enumerate(ordered)}
   esm=embedding([unique[n]['sequence'] for n in ordered],length)
   base=prediction_batch(requests,length,seed=config['seed'],decoder_scale=decoder.fm.scale_ref)
   return (esm[torch.tensor([index[r['id']] for r,_ in requests],device='cuda')],*base[1:])
  def predict(requests,length):
   conditioning_ids=[r['id'] for r,_ in requests] if config.get('reuse_sample_conditioning') else None
   return infer(model,decoder,tensors(requests,length),cfg,conditioning_ids=conditioning_ids,**options)
  telemetry=Telemetry(a.output,True)
  # These controls include changes in ESMC batch size and padding, not just the head.
  with torch.no_grad():
   for length,requests in buckets.items():
    count=batches[length]
    chunk=requests[:count-3]+requests[-3:] if len(requests)>count else requests
    _,ca,_=predict(chunk,length);whole=ca.cpu().numpy();del ca
    for i in (0,len(chunk)-3):
     r,k=chunk[i];n=len(r['sequence']);_,ca,_=predict([(r,k)],n)
     metrics=ca_metrics(whole[i,:n],ca[0].cpu().numpy());delta=abs(ca_metrics(whole[i,:n],r['ca'].numpy())['ca_lddt']-ca_metrics(ca[0].cpu().numpy(),r['ca'].numpy())['ca_lddt'])
     control=dict(target_id=r['id'],bucket=length,batch=len(chunk),reference_ca_lddt_absolute_change=delta,**metrics);manifest['controls'].append(control);atomic_json(a.output/'manifest.json',manifest);print('online control',json.dumps(control),flush=True)
     del ca
     if metrics['ca_rmsd']>.2 or metrics['ca_lddt']<.99 or delta>.005:raise ValueError('online batch/padding control failed')
   scorers=ProcessPoolExecutor(max_workers=1,mp_context=multiprocessing.get_context('spawn'));futures=[]
   with h5py.File(a.output/'predictions.h5','x') as output:
    for length,requests in buckets.items():
     for offset in range(0,len(requests),batches[length]):
      if time.monotonic()-start>1500:raise TimeoutError('25-minute work cap')
      chunk=requests[offset:offset+batches[length]];torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();nvtx=f'collect::online::{length}::{offset}'
      torch.cuda.nvtx.range_push(nvtx)
      try:
       z,ca,backbone=predict(chunk,length)
       z,ca,backbone=[x.float().cpu().numpy() for x in (z,ca,backbone)]
       torch.cuda.synchronize();seconds=time.monotonic()-tick
      finally:torch.cuda.nvtx.range_pop()
      futures.append(scorers.submit(score_batch,[(setting,r['id'],k,ca[i,:len(r['sequence'])],r['ca'].numpy(),backbone[i,:len(r['sequence'])],str(a.usalign.resolve())) for i,(r,k) in enumerate(chunk)]))
      write_batch(output,setting,chunk,z,ca,backbone)
      manifest['completed_predictions']+=len(chunk);manifest['batches'].append(dict(nvtx_range=nvtx,length=length,batch=len(chunk),proteins=len(chunk)//3,seconds=seconds,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved()))
      atomic_json(a.output/'manifest.json',manifest);print('online predictions',manifest['completed_predictions'],flush=True)
   rows=[r for f in futures for r in f.result()]
   if len(rows)!=1878 or {(r['target_id'],r['sample']) for r in rows}!={(n,k) for n in ids for k in range(3)}:raise ValueError('incomplete online coverage')
   write_scores(a.output,manifest,rows,time.monotonic()-start,str(a.usalign.resolve()),'overlapped CPU scoring')
   manifest['status']='complete'
 except BaseException as error:manifest.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:
  if scorers:scorers.shutdown(wait=True,cancel_futures=True)
  if telemetry:telemetry.close()
  manifest['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',manifest)


if __name__=='__main__':main()
