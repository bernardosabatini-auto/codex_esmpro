"""Quality checks for cached conditional endpoint augmentation."""
import numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from audit_fragment_teacher_targets import proper_rmsd_batch


def qualifying_states(decoded,source,fragment,start,indices):
    valid=backbone_geometry(decoded)['coarse_valid'];rows=[];accepted=[]
    for index in indices:
        index=int(index);rmsd=float(proper_rmsd_batch(decoded[index:index+1,:,1],source[index,:,1])[0]);fit=motif_fit(decoded[index],fragment,int(start));ok=bool(valid[index] and rmsd<=1 and fit['motif_ca_rmsd']<=1 and fit['motif_drms']<=1)
        rows.append(dict(candidate_index=index,coarse_valid=bool(valid[index]),whole_rmsd=rmsd,**fit,accepted=ok))
        if ok:accepted.append(index)
    return accepted,rows


def maximum_scaffold_difference(decoded,indices,start,motif_length):
    if len(indices)<2:return None
    bb=decoded[indices,:,1];keep=np.ones(bb.shape[1],bool);keep[start:start+motif_length]=False
    return max(float(proper_rmsd_batch(bb[i+1:,keep],bb[i,keep]).max()) for i in range(len(bb)-1))
