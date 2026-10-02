"""Scaffold fragment-only codes; compare unchanged full-context numerical controls."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.backbone import encode_backbone
from latentfold.flow import target_noise
from latentfold.generative import sample_unconditional
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from diagnose_pca_frames import frame
from generate_generative_pilot import motif_error
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def canonical_fragment(fragment):
    # Accept only the cropped coordinates. No scaffold-dependent frame input.
    basis,degenerate=frame(fragment[:,1]);return ((fragment-fragment[:,1].mean(0))@basis).astype(np.float32),degenerate


def main():
 p=argparse.ArgumentParser()
 for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();c=json.loads(a.config.read_text())
 for key in ('protocol','parent_manifest','parent_predictions','selection','checkpoint','decoder_checkpoint'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 rows=json.loads(Path(c['selection']).read_text())['rows']
 if len(rows)!=16 or c['samples']!=4:raise ValueError('Unexpected panel')
 a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],fragments=[],records=[],batches=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
 try:
  torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);telemetry=Telemetry(a.output,True)
  with torch.no_grad(),inference_precision('fp32'),h5py.File(c['parent_predictions']) as parent,h5py.File(a.output/'predictions.h5','x') as out:
   for row in rows:
    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Isolated motif cap')
    ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;raw=np.asarray(row['reference']['backbone'],dtype=np.float32)[st:st+k].copy();fragment,degenerate=canonical_fragment(raw);rot=np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float32);posed,_=canonical_fragment(raw@rot+np.array([11,7,-3],np.float32));fm=torch.ones(1,k,dtype=torch.bool,device='cuda');z=F.layer_norm(encode_backbone(decoder,torch.from_numpy(fragment)[None].cuda(),fm),(8,));zp=F.layer_norm(encode_backbone(decoder,torch.from_numpy(posed)[None].cuda(),fm),(8,));control=dict(kind='fragment_pose',target_id=ident,coordinate_max_abs=float(np.max(np.abs(fragment-posed))),latent_rmse=float((z-zp).square().mean().sqrt()));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
    if control['coordinate_max_abs']>1e-4 or control['latent_rmse']>1e-4:raise ValueError('Fragment rigid-pose invariance failed')
    dn=target_noise([ident],[4*k],3,seed=c['seed'],sample_index=0,stream='fragment_decoder:0',device='cuda')*decoder.fm.scale_ref;_,rt=decoder(z,fm,noise=dn,return_backbone=True);roundtrip=rt[0].cpu().numpy();record=dict(target_id=ident,length=n,fragment_length=k,start=st,near_degenerate=degenerate,roundtrip_drms=float(motif_error(roundtrip[None],fragment,np.ones(k,dtype=bool))[0]),**ca_metrics(roundtrip[:,1],fragment[:,1]));m['fragments'].append(record);g=out.create_group(ident);g.create_dataset('fragment',data=fragment);g.create_dataset('fragment_latent',data=z[0].cpu().numpy());g.create_dataset('fragment_roundtrip',data=roundtrip)
    b=4;mask=torch.ones(b,n,dtype=torch.bool,device='cuda');esm=torch.zeros(b,n,2560,device='cuda');keep=torch.zeros_like(mask);keep[:,st:st+k]=True;target=torch.zeros(b,n,8,device='cuda');target[:,st:st+k]=z
    def noises(stream,index=0,width=8,mult=1):return torch.cat([target_noise([ident],[mult*n],width,seed=c['seed'],sample_index=i,stream=stream+':'+str(index),device='cuda') for i in range(b)])
    noise=noises('flow');eps=noises('motif');dn=noises('decoder',width=3,mult=4)*decoder.fm.scale_ref
    def fresh(i,j):return noises('refinement',i*2+j)
    if ident in c['control_ids']:
     full=torch.from_numpy(parent['references/'+ident+'/latent'][:])[None].cuda().expand(b,-1,-1);cz=sample_unconditional(model,esm,mask,noise=noise,steps=50,fixed=(full,keep),motif_noise=eps,repaint=3,fresh_noise=fresh);_,cbb=decoder(cz,mask,noise=dn,return_backbone=True);expected=parent['original50/motif_u3/'+ident];g.create_dataset('full_control',data=cbb.cpu().numpy())
     for slot in range(b):
      control=dict(kind='full_context',target_id=ident,slot=slot,latent_max_abs=float(np.max(np.abs(cz[slot].cpu().numpy()-expected['latent'][slot]))),validity_identical=bool(backbone_geometry(cbb[slot:slot+1].cpu().numpy())['coarse_valid'][0])==bool(backbone_geometry(expected['backbone'][slot:slot+1])['coarse_valid'][0]),**ca_metrics(cbb[slot,:,1].cpu().numpy(),expected['backbone'][slot,:,1]));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
      if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.2 or control['ca_lddt']<.99 or not control['validity_identical']:raise ValueError('Full-context parent control failed')
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();result=sample_unconditional(model,esm,mask,noise=noise,steps=50,fixed=(target,keep),motif_noise=eps,repaint=3,fresh_noise=fresh);_,bb=decoder(result,mask,noise=dn,return_backbone=True);torch.cuda.synchronize();seconds=time.monotonic()-tick;bb=bb.cpu().numpy();g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=result.cpu().numpy());reference=np.zeros((n,4,3),np.float32);reference[st:st+k]=fragment;errors=motif_error(bb,reference,keep[0].cpu().numpy());geometry=backbone_geometry(bb)
    for slot in range(b):m['records'].append(dict(target_id=ident,family=row['family'],slot=slot,motif_drms=float(errors[slot]),coarse_valid=bool(geometry['coarse_valid'][slot])))
    m['batches'].append(dict(target_id=ident,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()));out.flush();atomic_json(a.output/'manifest.json',m);print('fragment',ident,record,'motif',errors.tolist(),flush=True)
  m['status']='complete'
 except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:
  if telemetry:telemetry.close()
  m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)
if __name__=='__main__':main()
