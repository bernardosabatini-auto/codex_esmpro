"""A motif and global fold must coexist in one physically screened refold."""
import numpy as np
from .metrics import ca_metrics


def motif_fit(backbone, fragment, start):
    bb,ref=np.asarray(backbone),np.asarray(fragment)
    if bb.ndim!=3 or bb.shape[1:]!=(4,3) or ref.ndim!=3 or ref.shape[1:]!=(4,3) or len(ref)<3 or type(start) is not int or start<0 or start+len(ref)>len(bb):
        raise ValueError('Matching complete backbone fragment and valid placement required')
    x=bb[start:start+len(ref),1];y=ref[:,1]
    if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Nonfinite motif')
    dx=np.linalg.norm(x[:,None]-x[None,:],axis=-1);dy=np.linalg.norm(y[:,None]-y[None,:],axis=-1)
    return dict(motif_drms=float(np.sqrt(np.mean((dx-dy)**2))),motif_ca_rmsd=ca_metrics(x,y)['ca_rmsd'])


def same_refold_success(raw, refolds):
    if not refolds:raise ValueError('All attempted refolds must be supplied')
    for r in [raw]+list(refolds):
        for key in ('motif_drms','motif_ca_rmsd'):
            if not np.isfinite(r[key]) or r[key]<0:raise ValueError('Invalid motif score')
        if r['coarse_valid'] not in (True,False,0,1):raise ValueError('Invalid geometry flag')
    if any(not np.isfinite(r['sc_tm']) or not 0<=r['sc_tm']<=1 for r in refolds):raise ValueError('Invalid global agreement')
    same=[i for i,r in enumerate(refolds) if r['sc_tm']>.5 and r['coarse_valid'] and r['motif_drms']<=1 and r['motif_ca_rmsd']<=1]
    legacy=[i for i,r in enumerate(refolds) if r['sc_tm']>.5 and r['coarse_valid'] and r['motif_drms']<=1]
    raw_ok=bool(raw['coarse_valid'] and raw['motif_drms']<=1 and raw['motif_ca_rmsd']<=1)
    return dict(raw_gate_passed=raw_ok,strict_joint_success=raw_ok and bool(same),successful_refold_indices=same,legacy_drms_joint_success=bool(raw['coarse_valid'] and raw['motif_drms']<=1 and legacy),valid_designable=bool(raw['coarse_valid'] and any(r['sc_tm']>.5 and r['coarse_valid'] for r in refolds)))


def first_repaired_target(raw,refolds):
    """A same-refold training label, distinct from raw motif retention success."""
    outcome=same_refold_success(raw,refolds)
    if not raw['coarse_valid'] or not outcome['successful_refold_indices']:return None
    return outcome['successful_refold_indices'][0]
