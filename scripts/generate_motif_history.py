"""Matched inner-history refresh with cached isolated-fragment codes."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.generative import sample_unconditional
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from latentfold.fragment_designability import motif_error
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
 p=argparse.ArgumentParser()
 for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();c=json.loads(a.config.read_text())
 for key in ('protocol','parent_manifest','parent_predictions','selection','checkpoint','decoder_checkpoint'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 rows=json.loads(Path(c['selection']).read_text())['rows']
 if len(rows)!=16 or c['samples']!=4 or c['steps']!=50 or c['repaint']!=3 or c['update_history_each_eval'] is not True:raise ValueError('Changed recipe')
 a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],records=[],batches=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
 try:
  torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
  if not model.self_cond:raise ValueError('History experiment requires self-conditioning')
  decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);telemetry=Telemetry(a.output,True)
  with torch.no_grad(),inference_precision('fp32'),h5py.File(c['parent_predictions']) as parent,h5py.File(a.output/'predictions.h5','x') as out:
   for row in rows:
    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('History profile cap')
    ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;fragment=parent[ident+'/fragment'][:];z=torch.from_numpy(parent[ident+'/fragment_latent'][:]).cuda();b=4;mask=torch.ones(b,n,dtype=torch.bool,device='cuda');esm=torch.zeros(b,n,2560,device='cuda');keep=torch.zeros_like(mask);keep[:,st:st+k]=True;target=torch.zeros(b,n,8,device='cuda');target[:,st:st+k]=z;g=out.create_group(ident)
    def noises(stream,index=0,width=8,mult=1):return torch.cat([target_noise([ident],[mult*n],width,seed=c['seed'],sample_index=i,stream=stream+':'+str(index),device='cuda') for i in range(b)])
    noise=noises('flow');eps=noises('motif');dn=noises('decoder',width=3,mult=4)*decoder.fm.scale_ref
    def fresh(i,j):return noises('refinement',i*2+j)
    kwargs=dict(noise=noise,steps=50,fixed=(target,keep),motif_noise=eps,repaint=3,fresh_noise=fresh)
    if ident in c['control_ids']:
     cz=sample_unconditional(model,esm,mask,**kwargs);_,cbb=decoder(cz,mask,noise=dn,return_backbone=True);expected=parent[ident];g.create_dataset('baseline_control',data=cbb.cpu().numpy());g.create_dataset('baseline_control_latent',data=cz.cpu().numpy())
     for slot in range(b):
      control=dict(target_id=ident,slot=slot,latent_max_abs=float(np.max(np.abs(cz[slot].cpu().numpy()-expected['latent'][slot]))),validity_identical=bool(backbone_geometry(cbb[slot:slot+1].cpu().numpy())['coarse_valid'][0])==bool(backbone_geometry(expected['backbone'][slot:slot+1])['coarse_valid'][0]),**ca_metrics(cbb[slot,:,1].cpu().numpy(),expected['backbone'][slot,:,1]));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
      if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.2 or control['ca_lddt']<.99 or not control['validity_identical']:raise ValueError('Baseline output identity failed')
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();result=sample_unconditional(model,esm,mask,**kwargs,update_history_each_eval=True);_,bb=decoder(result,mask,noise=dn,return_backbone=True);torch.cuda.synchronize();seconds=time.monotonic()-tick;bb=bb.cpu().numpy();g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=result.cpu().numpy());reference=np.zeros((n,4,3),np.float32);reference[st:st+k]=fragment;errors=motif_error(bb,reference,keep[0].cpu().numpy());geometry=backbone_geometry(bb)
    for slot in range(b):m['records'].append(dict(target_id=ident,family=row['family'],slot=slot,motif_drms=float(errors[slot]),coarse_valid=bool(geometry['coarse_valid'][slot])))
    m['batches'].append(dict(target_id=ident,seconds=seconds,velocity_evaluations=148,peak_reserved_bytes=torch.cuda.max_memory_reserved()));out.flush();atomic_json(a.output/'manifest.json',m);print('history',ident,'motif',errors.tolist(),'valid',geometry['coarse_valid'].tolist(),flush=True)
  m['status']='complete'
 except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:
  if telemetry:telemetry.close()
  m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)
if __name__=='__main__':main()
