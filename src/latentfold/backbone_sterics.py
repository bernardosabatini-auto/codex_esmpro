"""Nonbonded backbone pairs touching editable residues, excluding 1–4 terms."""
from functools import lru_cache
import numpy as np
import torch


@lru_cache(maxsize=128)
def _pairs(length,residues):
    if length<2 or not residues or any(not 0<=r<length for r in residues):raise ValueError('Contained editable residues required')
    neighbors=[set() for _ in range(4*length)]
    bonds=[(4*r+a,4*r+b) for r in range(length) for a,b in ((0,1),(1,2),(2,3))]
    bonds += [(4*r+2,4*(r+1)) for r in range(length-1)]
    for a,b in bonds:neighbors[a].add(b);neighbors[b].add(a)
    editable=np.array([4*r+a for r in residues for a in range(4)])
    all_atoms=np.arange(4*length);is_editable=np.isin(all_atoms,editable);rows=[]
    for atom in editable:
        excluded={int(atom)};front={int(atom)}
        for _ in range(3):
            front={j for i in front for j in neighbors[i]}-excluded;excluded|=front
        keep=~np.isin(all_atoms,list(excluded))&((all_atoms>atom)|~is_editable)
        rows.extend((min(int(atom),int(other)),max(int(atom),int(other))) for other in all_atoms[keep])
    return np.asarray(sorted(rows),dtype=np.int64).reshape(-1,2)


def nonbonded_pairs(length,residues):
    return _pairs(length,tuple(sorted(set(residues)))).copy()


def steric_audit(backbone,residues,threshold=1.5):
    x=np.asarray(backbone,dtype=np.float64)
    if x.ndim!=3 or x.shape[1:]!=(4,3) or not np.isfinite(x).all():raise ValueError('Finite N/CA/C/O backbone required')
    indices=nonbonded_pairs(len(x),residues);flat=x.reshape(-1,3)
    d=np.linalg.norm(flat[indices[:,0]]-flat[indices[:,1]],axis=-1)
    return dict(pairs=len(indices),pairs_below_threshold=int((d<threshold).sum()),threshold_angstrom=threshold,
                minimum_distance=float(d.min()) if len(d) else None)


def steric_loss(backbone,indices,cutoffs,*,scale,editable_atoms):
    """Violation mass per editable atom, not diluted by all possible pairs."""
    if scale<=0 or editable_atoms<=0:raise ValueError('Positive scales required')
    x=backbone.reshape(-1,3);d=(x[indices[:,0]]-x[indices[:,1]]).norm(dim=-1)
    return ((cutoffs-d).clamp_min(0)/scale).square().sum()/editable_atoms
