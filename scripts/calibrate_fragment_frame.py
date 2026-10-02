"""Paired original/anchored reconstructions; diagnostic, never a gate override."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from prepare_overfit import sha
from profile_gpu import atomic_json


def scores(bb, raw, fragment, start):
    return dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),
                global_rmsd=ca_metrics(bb[:,1],raw[:,1])['ca_rmsd'],
                motif_rmsd=ca_metrics(bb[start:start+len(fragment),1],fragment[:,1])['ca_rmsd'])


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','data_manifest','data_report','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed calibration source')
    d=json.loads(Path(c['data_manifest']).read_text())
    if d['status']!='complete' or c['seed']!=d['config']['seed']:raise ValueError('Unmatched reconstruction seed')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as src,h5py.File(a.output/'reconstructions.h5','x') as out:
            for ident,g in src['train'].items():
                raw=g['reference_backbone'][:];n=len(raw);mask=torch.ones(1,n,dtype=torch.bool,device='cuda');z=torch.from_numpy(g['reference_z'][:])[None].cuda()
                for condition,q in g['conditions'].items():
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Calibration cap')
                    noise=target_noise([ident],[4*n],3,seed=c['seed'],stream='anchored_target:'+condition,device='cuda')*decoder.fm.scale_ref
                    _,bb=decoder(z,mask,noise=noise,return_backbone=True);bb=bb[0].cpu().numpy();out.create_dataset(ident+'/'+condition,data=bb)
                    args=(raw,q['fragment'][:],int(q.attrs['start']))
                    m['records'].append(dict(target_id=ident,condition=condition,original=scores(bb,*args),anchored=scores(q['target_roundtrip'][:],*args)))
                out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',predictions_sha256=sha(a.output/'reconstructions.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
