"""Add conditional target codes without changing any supplied fragment input."""
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
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','probe_report','probe_manifest','parent_manifest','base_fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed source')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],encoding_controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['base_fragments']) as src,h5py.File(a.output/'fragments.h5','x') as out:
            if len(src['train'])!=32 or len(src['development'])!=16:raise ValueError('Wrong base corpus')
            for name in src:src.copy(src[name],out,name=name)
            for ident,g in out['train'].items():
                raw=g['reference_backbone'][:];n=len(raw);mask=torch.ones(1,n,dtype=torch.bool,device='cuda');fresh=F.layer_norm(encode_backbone(decoder,torch.from_numpy(raw)[None].cuda(),mask),(8,));error=float((fresh-torch.from_numpy(g['reference_z'][:])[None].cuda()).square().mean().sqrt());m['encoding_controls'].append(dict(target_id=ident,latent_rmse=error))
                if error>.05:raise ValueError('Cached source encoding mismatch')
                for condition,q in g['conditions'].items():
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Target encoding cap')
                    aligned=anchor_backbone(raw,q['fragment'][:],int(q.attrs['start']));z=F.layer_norm(encode_backbone(decoder,torch.from_numpy(aligned)[None].cuda(),mask),(8,));q.create_dataset('target_latent',data=z[0].cpu().numpy());noise=target_noise([ident],[4*n],3,seed=c['seed'],stream='anchored_target:'+condition,device='cuda')*decoder.fm.scale_ref;_,bb=decoder(z,mask,noise=noise,return_backbone=True);bb=bb[0].cpu().numpy();q.create_dataset('target_roundtrip',data=bb);row=dict(target_id=ident,condition=condition,coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**ca_metrics(bb[:,1],raw[:,1]));m['records'].append(row)
                    if condition=='f30_center':
                        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=float);posed=anchor_backbone(raw.astype(float)@rotation+np.array([11,7,-3]),q['fragment'][:],int(q.attrs['start']));zp=F.layer_norm(encode_backbone(decoder,torch.from_numpy(posed)[None].cuda(),mask),(8,));control=dict(target_id=ident,coordinate_max_abs=float(np.max(abs(aligned-posed))),latent_rmse=float((z-zp).square().mean().sqrt()));m['controls'].append(control)
                        if control['coordinate_max_abs']>1e-4 or control['latent_rmse']>1e-4:raise ValueError('Anchored target pose dependence')
                out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',fragments_sha256=sha(a.output/'fragments.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
