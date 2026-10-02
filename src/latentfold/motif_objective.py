"""Pose-independent motif objective using only supplied fragment coordinates."""
import torch


def motif_distance_mse(backbone, fragment, start):
    """Mean squared error of the fragment's complete CA distance matrix, in A^2."""
    if backbone.ndim!=4 or backbone.shape[2:]!=(4,3) or fragment.ndim!=3 or fragment.shape[1:]!=(4,3):
        raise ValueError('Expected backbone [B,L,4,3] and fragment [M,4,3]')
    if type(start) is not int or start<0 or len(fragment)<3 or start+len(fragment)>backbone.shape[1]:
        raise ValueError('Invalid fragment placement')
    if backbone.device!=fragment.device or not torch.isfinite(backbone).all() or not torch.isfinite(fragment).all():
        raise ValueError('Invalid coordinates/device')
    x=backbone[:,start:start+len(fragment),1];y=fragment[:,1]
    dx=torch.linalg.vector_norm(x[:,:,None]-x[:,None,:],dim=-1)
    dy=torch.linalg.vector_norm(y[:,None]-y[None,:],dim=-1)
    return (dx-dy).square().mean((1,2))
