"""Measure fragment-anchored label compatibility and reconstruction, no training."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.fragment_frame import anchor_backbone
from latentfold.backbone import encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from prepare_fragment_feedback import selected_ids
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','parent_manifest','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed frame source')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],encoding_controls=[],pose_controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as f,h5py.File(a.output/'predictions.h5','x') as out:
            if c['training_ids']!=selected_ids(f):raise ValueError('Changed training-only panel')
            for ident in c['training_ids']:
                g=f['train/'+ident];raw=g['reference_backbone'][:];original=g['reference_z'][:];n=len(raw);mask=torch.ones(1,n,dtype=torch.bool,device='cuda');fresh=F.layer_norm(encode_backbone(decoder,torch.from_numpy(raw)[None].cuda(),mask),(8,));parity=float((fresh-torch.from_numpy(original)[None].cuda()).square().mean().sqrt());m['encoding_controls'].append(dict(target_id=ident,latent_rmse=parity))
                if parity>.05:raise ValueError('Original cached frame parity failed')
                for condition in c['conditions']:
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Frame probe cap')
                    q=g['conditions/'+condition];fragment=q['fragment'][:];st=int(q.attrs['start']);k=len(fragment);aligned=anchor_backbone(raw,fragment,st);z=F.layer_norm(encode_backbone(decoder,torch.from_numpy(aligned)[None].cuda(),mask),(8,));zz=z[0].cpu().numpy();latent=q['latent'][:];row=dict(target_id=ident,family=str(g.attrs['family']),condition=condition,latent_before_rmse=float(np.sqrt(np.mean((original[st:st+k]-latent)**2))),latent_after_rmse=float(np.sqrt(np.mean((zz[st:st+k]-latent)**2))),full_target_latent_change_rmse=float(np.sqrt(np.mean((zz-original)**2))))
                    if condition=='f30_center':
                        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64);recovered=anchor_backbone(raw.astype(float)@rotation+np.array([11,7,-3]),fragment,st);zp=F.layer_norm(encode_backbone(decoder,torch.from_numpy(recovered)[None].cuda(),mask),(8,));control=dict(target_id=ident,coordinate_max_abs=float(np.max(abs(aligned-recovered))),latent_rmse=float((z-zp).square().mean().sqrt()));m['pose_controls'].append(control)
                        if control['coordinate_max_abs']>1e-4 or control['latent_rmse']>1e-4:raise ValueError('Fragment-anchor pose control failed')
                    out.create_dataset(ident+'/'+condition+'/latent',data=zz);noise=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='fragment_frame:'+condition,device='cuda')*decoder.fm.scale_ref
                    for mode,codes in [('original',torch.from_numpy(original)[None].cuda()),('anchored',z)]:
                        _,bb=decoder(codes,mask,noise=noise,return_backbone=True);bb=bb[0].cpu().numpy();out.create_dataset(ident+'/'+condition+'/'+mode,data=bb);row[mode]=dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**ca_metrics(bb[:,1],raw[:,1]))
                    m['records'].append(row);out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
