"""Deterministic selection and unchanged metadata eligibility for new labels."""
import math
import numpy as np
from latentfold.teacher_states import definition
from latentfold.audit_bounds import teacher_priors


def profile_rows(rows):
    if len({r['id'] for r in rows}) != len(rows) or len({r['family'] for r in rows}) != len(rows):
        raise ValueError('duplicate candidate identity or family')
    selected=[]
    for bucket in (128,256,384,512):
        group=sorted((r for r in rows if r['bucket']==bucket),key=lambda r:(r['length'],r['id']))
        if len(group)<4:raise ValueError('insufficient bucket candidates')
        selected.extend(group[k*(len(group)-1)//3] for k in range(4))
    return selected


def capacity_ids(rows,count=32):
    """Round-robin length strata, ID order, without student/audit scores."""
    if count<1 or len(rows)<count or len({r['id'] for r in rows})!=len(rows) or any(r['bucket'] not in (128,256,384,512) for r in rows):raise ValueError('insufficient or invalid distinct capacity candidates')
    queues={b:sorted(r['id'] for r in rows if r['bucket']==b) for b in (128,256,384,512)}
    result=[]
    while len(result)<count:
        for b in queues:
            if queues[b] and len(result)<count:result.append(queues[b].pop(0))
    return result


def eligibility(backbone, valid, confidence):
    confidence=np.asarray(confidence);valid=np.asarray(valid,dtype=bool)
    n=backbone.shape[1]
    if confidence.shape!=(16,n) or not np.isfinite(confidence).all() or confidence.min()<0 or confidence.max()>1:
        raise ValueError('invalid teacher confidence')
    if confidence.mean()<.8:return None,'mean_confidence'
    if (confidence.mean(0)>=.7).sum()<max(32,math.ceil(n/2)):return None,'confident_core'
    if valid.sum()<2:return None,'too_few_valid'
    state=definition(backbone,valid,confidence)
    if state is None or state['states']<2:return None,'single_state'
    if state['states']>8:return None,'too_many_states'
    if state['mean_pair_distance']>6:return None,'excessive_state_distance'
    return state,None


def reconstruction_summary(rows):
    eligible=[r for r in rows if r.get('eligible')]
    if not eligible:return dict(targets=0,gate_passed=False,priors={})
    out={}
    for prior in ('empirical','balanced'):
        values=[]
        for r in eligible:
            w=teacher_priors(r['state_definition'])[prior]
            audit=r['reconstruction']
            ld=np.asarray(audit['ca_lddt']);valid=np.asarray(audit['coarse_valid'])
            if ld.shape!=(16,) or valid.shape!=(16,) or not np.isfinite(ld).all() or ((ld<0)|(ld>1)).any():
                raise ValueError('incomplete reconstruction audit')
            values.append((float(w@ld),float(w@valid)))
        mean=np.mean(values,axis=0);out[prior]=dict(ca_lddt=float(mean[0]),valid=float(mean[1]))
    return dict(targets=len(eligible),priors=out,gate_passed=all(v['ca_lddt']>=.98 and v['valid']>=.99 for v in out.values()))
