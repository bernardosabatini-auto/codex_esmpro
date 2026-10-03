"""Bound crossed flow/decoder noise diagnostic and exact variance identities."""
import json
from pathlib import Path
import numpy as np
from prepare_overfit import sha


def variance_components(values,target):
    x=np.asarray(values,dtype=np.float64);y=np.asarray(target,dtype=np.float64)
    if x.ndim!=3 or x.shape[0]<2 or x.shape[1]<2 or y.shape!=(x.shape[2],) or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Finite crossed latent/decoder distance vectors required')
    latent_mean=x.mean(1);grand=x.mean((0,1))
    error=float(np.mean((x-y)**2));systematic=float(np.mean((latent_mean-y)**2));within=float(np.mean((x-latent_mean[:,None])**2))
    between=float(np.mean((latent_mean-grand)**2));total=float(np.mean((x-grand)**2))
    if not np.isclose(error,systematic+within,rtol=1e-10,atol=1e-12) or not np.isclose(total,between+within,rtol=1e-10,atol=1e-12):raise ValueError('Variance identity failed')
    return dict(mean_squared_distance_error=error,systematic_distance_error=systematic,within_latent_decoder_variance=within,between_latent_variance=between,total_variance=total,
                decoder_fraction_of_error=within/error if error else None,decoder_fraction_of_variance=within/total if total else None)


def motif_distances(backbone,start,length=20):
    ca=np.asarray(backbone,dtype=np.float64)[...,start:start+length,1,:]
    i,j=np.triu_indices(length,1)
    return np.linalg.norm(ca[...,i,:]-ca[...,j,:],axis=-1)


def audit(c):
    from fragment_preference_calibration import audit_generation
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed crossed-decoder input')
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['baseline_manifest']).read_text());d=json.loads(Path(c['baseline_report']).read_text());bc=m['config'];audit_generation(bc)
    if (spec!=c['spec'] or Path(c['baseline_manifest']).parent.name!=spec['baseline_generation']
            or m['status']!='complete' or d['status']!='complete' or d['controls']!=68
            or d['manifest_sha256']!=sha(c['baseline_manifest']) or d['predictions_sha256']!=sha(c['baseline_predictions'])
            or c['baseline_predictions']!=str(Path(c['baseline_manifest']).parent/'predictions.h5')
            or (spec['targets'],spec['flow_samples'],spec['decoder_samples'],spec['decoder_steps'],spec['precision'],spec['decoder_stream'])!=(32,4,5,3,'fp32','decoder:0')
            or spec['seed']!=bc['spec']['seed'] or bc['arm']!='parent6000'
            or c['target_ids']!=bc['target_ids'] or c['selected']!=bc['selected']
            or c['fragments']!=bc['fragments'] or c['decoder_checkpoint']!=bc['decoder_checkpoint']
            or c['allocation_minutes']!=10 or c['work_cap_seconds']!=480):raise ValueError('Changed crossed-decoder recipe or baseline')
    if len(m['batches'])!=32 or any(r['peak_reserved_GiB']>75 for r in m['batches']):raise ValueError('Unqualified exact-length four-sample decoder profile')
    return spec
