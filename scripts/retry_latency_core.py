"""Reference-free bounded retry selection shared by all timed student heads."""
import numpy as np
from latentfold.ensemble_metrics import backbone_geometry


def bounded_outputs(draw,count,geometry=backbone_geometry):
    if type(count) is not int or not 1<=count<=32:raise ValueError('Expected prefix of the fixed32-output recipe')
    pending=list(range(count));selected=None;indices=np.arange(count);attempts=0
    for a in range(4):
        addresses=[k+32*a for k in pending];bb=draw(addresses)
        if bb.ndim!=4 or bb.shape[0]!=len(pending) or bb.shape[2:]!=(4,3) or not np.isfinite(bb).all():raise ValueError('Invalid attempted backbone')
        valid=geometry(bb)['coarse_valid'];attempts+=len(pending)
        if len(valid)!=len(pending):raise ValueError('Wrong validity count')
        if a==0:selected=bb.copy()
        remaining=[]
        for j,k in enumerate(pending):
            if valid[j]:selected[k]=bb[j];indices[k]=addresses[j]
            else:remaining.append(k)
        pending=remaining
        if not pending:break
    return selected,dict(attempts=attempts,exhausted=len(pending),selected_draws=indices.tolist())
