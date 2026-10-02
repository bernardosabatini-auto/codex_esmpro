"""Differentiate through the frozen original flow, with bounded activation memory.

This supplies numerical machinery only. Keeping a fixed Gaussian radius does
not prove that optimized samples retain designability or the prior distribution.
"""
import torch
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint


def unconditional_endpoint(net, noise, mask, *, steps=50, checkpoint_steps=True):
    if net.training or any(p.requires_grad for p in net.parameters()):raise ValueError('Frozen eval model required')
    if noise.shape!=(*mask.shape,8) or mask.dtype!=torch.bool or not mask.any(1).all() or not torch.isfinite(noise).all():raise ValueError('Invalid noise/mask')
    if type(steps) is not int or steps<1 or mask.shape[1]>net.pos.num_embeddings:raise ValueError('Invalid steps/length')
    b,n=mask.shape;esm=noise.new_zeros(b,n,net.cond_norm.normalized_shape[0]);drop=torch.ones(b,dtype=torch.bool,device=noise.device);kwargs={}
    if hasattr(net,'compute_pair'):kwargs['pair']=noise.new_zeros(b,n,n,net.null_pair.shape[-1])
    prepared=net.prepare_condition(esm,mask,drop,**kwargs);x=noise;sc=None;ts=torch.linspace(0,1,steps+1,device=noise.device)
    for i in range(steps):
        # Bind time values now: backward recomputation must not see the last loop time.
        def advance(current,history,t=ts[i],dt=ts[i+1]-ts[i]):
            v=net(current,t.expand(b),esm,mask,drop,history,prepared=prepared).float()
            following=current+(1-t)*v if net.self_cond else None
            return current+dt*v,following
        if checkpoint_steps and torch.is_grad_enabled() and x.requires_grad:x,sc=checkpoint(advance,x,sc,use_reentrant=False)
        else:x,sc=advance(x,sc)
    result=F.layer_norm(x,(8,))*mask[...,None]
    if not torch.isfinite(result).all():raise FloatingPointError('Nonfinite endpoint')
    return result


def normalized_gradient(gradient,mask):
    if gradient.shape!=(*mask.shape,8) or not torch.isfinite(gradient).all():raise ValueError('Invalid guidance gradient')
    g=gradient*mask[...,None];rms=(g.square().sum((1,2))/(8*mask.sum(1))).sqrt()
    return g/rms.clamp_min(1e-12)[:,None,None]


def project_radius(proposal,reference,mask):
    if proposal.shape!=reference.shape or proposal.shape!=(*mask.shape,8) or not torch.isfinite(proposal).all() or not torch.isfinite(reference).all():raise ValueError('Invalid proposal/reference')
    x=proposal*mask[...,None];ref=reference*mask[...,None];radius=ref.square().sum((1,2)).sqrt();current=x.square().sum((1,2)).sqrt()
    if (radius<=1e-12).any() or (current<=1e-12).any():raise ValueError('Degenerate radius')
    return x*(radius/current)[:,None,None]
