"""Heuristic decoder guidance of clean estimates, with detached flow history.

Unit-RMS gradients deliberately do not claim exact posterior sampling.
"""
import math
import torch
from torch.nn import functional as F
from latentfold.fragment_conditioning import prepare_fragment_condition, fragment_velocity
from latentfold.noise_guidance import normalized_gradient


@torch.no_grad()
def sample(net, adapter, features, keep, mask, *, noise, coordinates,
           objective, strength=.5, steps=50, first=25, stop=45, observe=None,
           derivative_check=None):
    if net.training or adapter.training or any(p.requires_grad for m in (net,adapter) for p in m.parameters()):
        raise ValueError('Frozen eval models required')
    if not math.isfinite(strength) or strength<0 or not 0<=first<stop<=steps:
        raise ValueError('Invalid guidance schedule')
    if noise.shape!=(*mask.shape,8) or not torch.isfinite(noise).all() or not mask.any(1).all():
        raise ValueError('Invalid sampling inputs')
    dropped=torch.zeros(len(mask),dtype=torch.bool,device=mask.device)
    esm,prepared=prepare_fragment_condition(net,adapter,features,keep,mask,dropped,coordinates=coordinates)
    x=noise.clone();history=None;ts=torch.linspace(0,1,steps+1,device=x.device)
    for i in range(steps):
        t,dt=ts[i],ts[i+1]-ts[i]
        def estimate(current):
            velocity=fragment_velocity(net,adapter,current,t.expand(len(x)),esm,mask,x_sc=history,prepared=prepared).float()
            clean=F.layer_norm(current+(1-t)*velocity,(8,))*mask[...,None]
            return velocity,clean
        direction=torch.zeros_like(x);loss=None
        if strength and first<=i<stop:
            with torch.enable_grad():
                current=x.detach().requires_grad_();v,z=estimate(current);loss=objective(z)
                if loss.shape!=(len(x),) or not torch.isfinite(loss).all():raise ValueError('Invalid per-example objective')
                gradient,=torch.autograd.grad(loss.sum(),current)
                if derivative_check is not None and i==first:
                    derivative_check(current,estimate,objective,loss.detach(),gradient.detach())
            direction=normalized_gradient(gradient.detach(),mask)
            v=v.detach();loss=loss.detach();del current,z,gradient
            weight=strength*(1-t)/t
        else:
            v,_=estimate(x);weight=x.new_zeros(())
        # History represents the original prior estimate, not an untrained
        # guided endpoint. There is no backward graph across time steps.
        following=(x+(1-t)*v).detach() if net.self_cond else None
        next_x=(x+dt*(v-weight*direction)).detach()
        if not torch.isfinite(next_x).all():raise FloatingPointError('Nonfinite guided state')
        if observe is not None:observe(i,x,v,direction,next_x,loss,float(weight),float(t),float(dt))
        x=next_x;history=following
    return F.layer_norm(x,(8,))*mask[...,None]
