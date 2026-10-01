"""Teacher-defined contact states for a learnability diagnostic, not biology."""
import numpy as np
from scipy.spatial.distance import cdist
from scipy.sparse.csgraph import connected_components


def definition(backbone, valid, confidence, *, max_features=4096):
    bb=np.asarray(backbone);valid=np.asarray(valid,dtype=bool);conf=np.asarray(confidence)
    if bb.ndim!=4 or bb.shape[2:]!=(4,3) or valid.shape!=(len(bb),) or conf.shape!=bb.shape[:2] or not np.isfinite(bb).all() or not np.isfinite(conf).all():
        raise ValueError('invalid teacher ensemble')
    indices=np.flatnonzero(valid)
    if len(indices)<2:raise ValueError('too few valid teachers')
    n=bb.shape[1];core=conf[valid].mean(0)>=.7
    if core.sum()<max(32,int(np.ceil(n*.5))):core=np.ones(n,dtype=bool)
    i,j=np.triu_indices(n,4);keep=core[i]&core[j];i,j=i[keep],j[keep]
    features=np.linalg.norm(bb[indices][:,i,1]-bb[indices][:,j,1],axis=-1)
    keep=(np.ptp(features,axis=0)>=2)&(features.min(0)<=12)
    i,j,features=i[keep],j[keep],features[:,keep]
    if len(i)>max_features:
        chosen=np.linspace(0,len(i)-1,max_features,dtype=int);i,j,features=i[chosen],j[chosen],features[:,chosen]
    if not len(i):return None
    distances=cdist(features,features)/np.sqrt(len(i))
    count,labels=connected_components(distances<=1.,directed=False)
    return dict(i=i.tolist(),j=j.tolist(),teacher_indices=indices.tolist(),features=features.tolist(),clusters=labels.tolist(),states=int(count),mean_pair_distance=float(distances[np.triu_indices(len(indices),1)].mean()),core_residues=int(core.sum()))


def contact_assignments(backbone, state, valid):
    bb=np.asarray(backbone);i,j=np.asarray(state['i']),np.asarray(state['j'])
    features=np.linalg.norm(bb[:,i,1]-bb[:,j,1],axis=-1)
    reference=np.asarray(state['features']);distance=cdist(features,reference)/np.sqrt(len(i));nearest=distance.argmin(1);errors=distance[np.arange(len(bb)),nearest]
    clusters=np.asarray(state['clusters'])[nearest];clusters=np.where((errors<=2.)&np.asarray(valid,dtype=bool),clusters,-1)
    return nearest,errors,clusters


def paired_change(candidate, reference, *, families=None):
    """Positive values always mean candidate minus comparator."""
    from .metrics import paired_comparison
    d=paired_comparison(reference,candidate,clusters=families)
    return dict(candidate=d['theirs'],reference=d['ours'],difference=d['theirs_minus_ours'],ci95=d['ci95'],families=d['clusters'] if families is not None else None,bootstrap_unit=d['bootstrap_unit'],targets=d['n'])


def audited_families(config):
    """Read the frozen training-family mapping, checking the label-manifest hash."""
    import hashlib,json
    from pathlib import Path
    raw=Path(config['label_manifest']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['label_manifest_sha256']:
        raise ValueError('label manifest changed before analysis')
    rows=json.loads(raw)['config']['targets']
    families={r['id']:r['family'] for r in rows}
    if len(families)!=len(rows) or any(not f for f in families.values()):
        raise ValueError('missing or duplicate family metadata')
    return families


def bridge_posterior(latents, clusters, chosen, noise, time):
    """Exact empirical-label posterior for x_t=(1-t)*N(0,I)+t*z.

    This is an oracle diagnostic knowing all target labels. It is not a learned
    model score and does not assume teacher frequencies are physical populations.
    """
    from scipy.special import logsumexp
    y=np.asarray(latents,dtype='float64');clusters=np.asarray(clusters,dtype=int);chosen=np.asarray(chosen,dtype=int);noise=np.asarray(noise,dtype='float64')
    if y.ndim!=2 or clusters.shape!=(len(y),) or noise.shape!=(len(chosen),y.shape[1]) or not 0<=time<1 or not np.isfinite(y).all() or not np.isfinite(noise).all():raise ValueError('invalid Gaussian bridge inputs')
    if (chosen<0).any() or (chosen>=len(y)).any() or (clusters<0).any():raise ValueError('invalid teacher or cluster index')
    gram=y@y.T;norm=np.diag(gram);ratio=time/(1-time)
    logits=ratio*(noise@y.T)+ratio**2*(gram[chosen]-.5*norm[None]);prob=np.exp(logits-logsumexp(logits,axis=1,keepdims=True));prob/=prob.sum(1,keepdims=True)
    state_prob=prob@np.eye(int(clusters.max())+1)[clusters];truth=clusters[chosen]
    entropy=np.maximum(0,-(state_prob*np.log2(np.maximum(state_prob,1e-300))).sum(1)).mean();mean_norm=np.einsum('bi,ij,bj->b',prob,gram,prob)
    floor=np.maximum(0,prob@norm-mean_norm).mean()/y.shape[1]/(1-time)**2
    return dict(oracle_state_accuracy=float((state_prob.argmax(1)==truth).mean()),true_state_posterior=float(state_prob[np.arange(len(truth)),truth].mean()),state_entropy_bits=float(entropy),oracle_velocity_mse_floor=float(floor))
