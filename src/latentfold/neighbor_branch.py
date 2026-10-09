"""Local derivative checks of a fixed ProteinMPNN neighbor branch.

These contexts restore the original dynamic graph and never change sampling.
"""
from contextlib import contextmanager
import torch


@contextmanager
def capture_neighbors(model):
    features=model.features;original=features._dist;captured={}
    def record(*args,**kwargs):
        values,indices=original(*args,**kwargs);captured['indices']=indices.detach().clone();return values,indices
    features._dist=record
    try:yield captured
    finally:features._dist=original


@contextmanager
def fixed_neighbors(model,indices):
    features=model.features;original=features._dist
    def fixed(points,mask,eps=1e-6):
        mask2=mask[:,:,None]*mask[:,None,:];delta=points[:,:,None]-points[:,None,:];d=mask2*torch.sqrt(delta.square().sum(-1)+eps);adjusted=d+(1-mask2)*d.max(-1,keepdim=True).values
        return torch.gather(adjusted,2,indices),indices
    features._dist=fixed
    try:yield
    finally:features._dist=original
