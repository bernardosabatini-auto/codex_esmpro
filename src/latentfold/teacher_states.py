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
