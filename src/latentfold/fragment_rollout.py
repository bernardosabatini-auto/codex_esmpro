"""Differentiate the production fragment sampler without changing its forward path."""
from contextlib import contextmanager
import torch
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
from .fragment_conditioning import prepare_fragment_condition
from .fragment_objective import proper_motif_mse
from .flow import target_noise


@contextmanager
def evaluation_modes(*roots):
    """Restore every submodule mode, including during checkpoint recomputation."""
    states={module:module.training for root in roots for module in root.modules()}
    try:
        for module in states:module.training=False
        yield
    finally:
        for module,mode in states.items():module.training=mode


def differentiable_sample_fragment(net,adapter,features,keep,mask,*,noise,steps=50,coordinates=None,checkpoint_velocity=True):
    if type(steps) is not int or steps<1 or noise.shape!=(*mask.shape,8) or not torch.isfinite(noise).all():raise ValueError('Finite correctly shaped noise and positive steps required')
    dropped=torch.zeros(len(mask),dtype=torch.bool,device=mask.device)
    with evaluation_modes(net,adapter):esm,prepared=prepare_fragment_condition(net,adapter,features,keep,mask,dropped,coordinates=coordinates)
    def velocity(x,t,history):
        with evaluation_modes(net):return net(x,t,esm,mask,x_sc=history,prepared=prepared).float()
    x,history=noise.clone(),None;ts=torch.linspace(0,1,steps+1,device=noise.device)
    for i in range(steps):
        t,dt=ts[i],ts[i+1]-ts[i]
        v=checkpoint(velocity,x,t.expand(len(x)),history,use_reentrant=False) if checkpoint_velocity else velocity(x,t.expand(len(x)),history)
        if net.self_cond:history=x+(1-t)*v
        x=x+dt*v
    z=F.layer_norm(x,(8,))*mask[...,None]
    if not torch.isfinite(z).all():raise FloatingPointError('Nonfinite differentiable sample')
    return z


def rollout_fragment_objective(net,adapter,decoder,features,keep,mask,coordinates,ids,lengths,dropped,*,step,seed=2026100243,maximum_examples=2):
    eligible=torch.where(~dropped)[0].tolist();stats=dict(motif_examples=0,motif_mse=0.,chosen_slots=[],velocity_evaluations=0)
    if not eligible:return None,stats
    rng=torch.Generator().manual_seed(seed+step);chosen=[eligible[i] for i in torch.randperm(len(eligible),generator=rng)[:maximum_examples].tolist()];nn=[lengths[i] for i in chosen];n=max(nn);ident=[f'{ids[i]}:slot{i}' for i in chosen];device=features.device
    noise=target_noise(ident,nn,8,seed=seed,sample_index=step,stream='rollout_flow',device=device);dn=target_noise(ident,[4*x for x in nn],3,seed=seed,sample_index=step,stream='rollout_decoder',device=device)*decoder.fm.scale_ref
    ff=features[chosen,:n];kk=keep[chosen,:n];mm=mask[chosen,:n];cc=coordinates[chosen,:n]
    z=differentiable_sample_fragment(net,adapter,ff,kk,mm,noise=noise,steps=50,coordinates=cc);ca=decoder(z,mm,noise=dn);loss=proper_motif_mse(ca,cc,kk)
    stats.update(motif_examples=len(chosen),motif_mse=float(loss.detach()),chosen_slots=chosen,velocity_evaluations=50,sample_velocity_evaluations=50*len(chosen),lengths=nn)
    return loss,stats
