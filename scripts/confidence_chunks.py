"""Bound confidence-head memory without changing trunk or diffusion draws."""
from contextlib import contextmanager
import torch


@contextmanager
def chunk_confidence(model,chunk=4):
    if type(chunk) is not int or chunk<1:raise ValueError('invalid confidence chunk')
    head=model.confidence_head;original=head.forward
    def forward(**kwargs):
        count=kwargs['num_diffusion_samples'];coords=kwargs['predicted_coords']
        if kwargs['single_inputs'].shape[0]!=1 or tuple(coords.shape[:-2]) not in ((count,),(1,count)):
            raise ValueError('confidence chunking supports exactly one protein')
        parts=[]
        for begin in range(0,count,chunk):
            size=min(chunk,count-begin);args=dict(kwargs,num_diffusion_samples=size,predicted_coords=coords.reshape(count,*coords.shape[-2:])[begin:begin+size]);values=original(**args)
            if any(not isinstance(v,torch.Tensor) or v.shape[0]!=size for v in values.values()):raise ValueError('unexpected confidence output batch')
            if parts and values.keys()!=parts[0].keys():raise ValueError('confidence output keys changed')
            parts.append(values)
        return {key:torch.cat([part[key] for part in parts],dim=0) for key in parts[0]}
    head.forward=forward
    try:yield
    finally:head.forward=original
