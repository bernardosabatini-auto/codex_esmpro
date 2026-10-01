"""Exact empirical-teacher flow as a positive control for sampling and decoding."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from scipy.special import logsumexp
from torch.nn import functional as F
from latentfold.flow import target_noise
from prepare_overfit import sha


def oracle_sample(teachers, noise, steps):
    y=np.asarray(teachers,dtype='float64');x=np.asarray(noise,dtype='float64').copy()
    if type(steps) is not int or steps<1 or y.ndim!=2 or x.ndim!=2 or y.shape[1]!=x.shape[1] or not len(y) or not np.isfinite(y).all() or not np.isfinite(x).all():raise ValueError('invalid oracle transport inputs')
    norm=(y*y).sum(1)
    for t in np.arange(steps)/steps:
        logits=(t/(1-t)**2)*(x@y.T)-.5*(t/(1-t))**2*norm[None]
        weights=np.exp(logits-logsumexp(logits,axis=1,keepdims=True));weights/=weights.sum(1,keepdims=True)
        x+=(weights@y-x)/(1-t)/steps
    return x.astype('float32')


def main():
    p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.labels.read_text());source=a.labels.parent/'labels.h5'
    if m['status']!='complete' or not m['training_gate_passed'] or sha(source)!=m['labels_sha256']:raise ValueError('audited label source required')
    a.output.mkdir(exist_ok=False,parents=True);start=time.monotonic();result=dict(status='running',source_manifest=str(a.labels.resolve()),source_manifest_sha256=sha(a.labels),source_labels_sha256=m['labels_sha256'],steps=[5,10,25,100],seed=2026100162,targets=[],scope='Oracle vector field knows all finite teacher latents. Positive sampling/decoder control, not a deployable sequence predictor.')
    with h5py.File(source) as src,h5py.File(a.output/'endpoints.h5','x') as out:
        for r in m['config']['targets']:
            ident=r['id'];g=src[ident];valid=g['coarse_valid'][:].astype(bool);n=r['length'];noise=torch.cat([target_noise([ident],[n],8,seed=result['seed'],sample_index=k) for k in range(32)]).numpy().reshape(32,-1);group=out.create_group(ident);diagnostic=[]
            for arm,key in [('aligned','teacher_z_aligned'),('pca','teacher_z_pca')]:
                teacher=g[key][:][valid].reshape(int(valid.sum()),-1)
                for steps in result['steps']:
                    z=oracle_sample(teacher,noise,steps).reshape(32,n,8);projected=F.layer_norm(torch.from_numpy(z),(8,)).numpy();group.create_dataset(f'{arm}_{steps}',data=projected)
                    rmse=np.sqrt(((projected.reshape(32,1,-1)-teacher[None])**2).mean(-1)).min(1)
                    diagnostic.append(dict(arm=arm,steps=steps,nearest_teacher_latent_rmse=float(rmse.mean())))
            result['targets'].append(dict(id=ident,diagnostics=diagnostic));print('oracle endpoints',len(result['targets']),flush=True)
    result.update(status='complete',endpoints_sha256=sha(a.output/'endpoints.h5'),elapsed_seconds=time.monotonic()-start);(a.output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
