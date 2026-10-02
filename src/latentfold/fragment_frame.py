"""Place a complete training target in the frame of its supplied fragment."""
import numpy as np


def anchor_backbone(backbone,fragment,start):
    bb,ref=np.asarray(backbone,dtype=np.float64),np.asarray(fragment,dtype=np.float64)
    if bb.ndim!=3 or bb.shape[1:]!=(4,3) or ref.ndim!=3 or ref.shape[1:]!=(4,3) or len(ref)<3 or type(start) is not int or start<0 or start+len(ref)>len(bb) or not np.isfinite(bb).all() or not np.isfinite(ref).all():raise ValueError('Finite complete backbone and contained supplied fragment required')
    x=bb[start:start+len(ref),1];y=ref[:,1];origin=x.mean(0);destination=y.mean(0);u,s,vh=np.linalg.svd((x-origin).T@(y-destination))
    if s[1]<1e-8:raise ValueError('Degenerate fragment alignment')
    rotation=u@np.diag([1.,1.,1. if np.linalg.det(u@vh)>0 else -1.])@vh;aligned=((bb-origin)@rotation+destination).astype(np.float32)
    if np.max(abs(aligned[start:start+len(ref)]-ref))>1e-4:raise ValueError('Fragment is not related by one proper rigid transform')
    return aligned
