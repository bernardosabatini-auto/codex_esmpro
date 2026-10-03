"""Bounded fixed-reference regression for refold-qualified training pairs.

Symmetric field construction inspired by https://arxiv.org/html/2609.09905v1 .
This fixed-reference variant makes no exact likelihood or KL claim for our
self-conditioned sampler with terminal latent normalization.
"""
import math
import torch
from .fragment_conditioning import prepare_fragment_condition, fragment_velocity


def anchored_branch_loss(positive, positive_reference, positive_target,
                         negative, negative_reference, negative_target,
                         mask, *, beta=.5, negative_weight=1.):
    if not math.isfinite(beta) or beta<=0 or not math.isfinite(negative_weight) or negative_weight<0:
        raise ValueError('Finite positive mixing and nonnegative branch weight required')
    if mask.dtype!=torch.bool or mask.ndim!=2 or not mask.any(1).all():raise ValueError('Nonempty valid-residue masks required')
    for x in (positive,positive_reference,positive_target,negative,negative_reference,negative_target):
        if x.shape!=(*mask.shape,8) or not torch.isfinite(x).all():raise ValueError('Finite matching flow fields required')
    if any(x.requires_grad for x in (positive_reference,negative_reference,positive_target,negative_target)):
        raise ValueError('Reference fields and endpoint targets must be fixed')
    def mse(x,target):return (((x-target).square().mean(-1)*mask).sum(1)/mask.sum(1)).mean()
    attractive=positive_reference+beta*(positive-positive_reference)
    mirrored=negative_reference-beta*(negative-negative_reference)
    pos=mse(attractive,positive_target);neg=mse(mirrored,negative_target)
    loss=pos+negative_weight*neg
    return loss,dict(positive_branch_loss=pos.detach(),negative_branch_loss=neg.detach(),
                     positive_flow_error=mse(positive,positive_target).detach(),
                     negative_flow_error=mse(negative,negative_target).detach())


def native_preference_flow_loss(net,adapter,reference_adapter,positive,negative,
                                features,keep,mask,*,coordinates,generator,beta=.5,negative_weight=1.):
    if any(p.requires_grad for p in net.parameters()) or any(p.requires_grad for p in reference_adapter.parameters()):
        raise ValueError('This experiment requires a frozen generator and reference adapter')
    if negative is None and negative_weight!=0:raise ValueError('A negative endpoint is required for contrastive training')
    if positive.requires_grad or (negative is not None and (negative.requires_grad or positive.shape!=negative.shape)) or positive.shape!=(*mask.shape,8):
        raise ValueError('Fixed matching native/generated latent endpoints required')
    if not torch.isfinite(positive).all() or (negative is not None and not torch.isfinite(negative).all()):raise ValueError('Nonfinite endpoint')
    noise=torch.randn(positive.shape,device=positive.device,generator=generator)
    t=torch.sigmoid(torch.randn(len(positive),device=positive.device,generator=generator)).clamp(1e-4,1-1e-4)
    history_enabled=bool(torch.rand((),device=positive.device,generator=generator)<.5)
    dropped=torch.zeros(len(positive),dtype=torch.bool,device=positive.device)
    esm,prepared=prepare_fragment_condition(net,adapter,features,keep,mask,dropped,coordinates=coordinates)
    with torch.no_grad():
        reference_esm,reference_prepared=prepare_fragment_condition(net,reference_adapter,features,keep,mask,dropped,coordinates=coordinates)
    tt=t[:,None,None]
    def branch(endpoint):
        x=(1-tt)*noise+tt*endpoint;target=endpoint-noise;history=None
        with torch.no_grad():
            if net.self_cond and history_enabled:
                history=x+(1-tt)*fragment_velocity(net,reference_adapter,x,t,reference_esm,mask,x_sc=None,prepared=reference_prepared)
            reference=fragment_velocity(net,reference_adapter,x,t,reference_esm,mask,x_sc=history,prepared=reference_prepared)
        current=fragment_velocity(net,adapter,x,t,esm,mask,x_sc=history,prepared=prepared)
        return current,reference,target
    p,pr,pt=branch(positive)
    if negative is None:
        # Reuse the exact scalar objective/validation with detached fields. This
        # executes one endpoint forward pass and supplies no negative labels.
        loss,info=anchored_branch_loss(p,pr,pt,p.detach(),pr,pt,mask,beta=beta,negative_weight=0.)
        info={k:v for k,v in info.items() if k.startswith('positive_')}
    else:
        n,nr,nt=branch(negative)
        loss,info=anchored_branch_loss(p,pr,pt,n,nr,nt,mask,beta=beta,negative_weight=negative_weight)
    info.update(noise=noise.detach(),t=t.detach(),self_conditioned=history_enabled)
    return loss,info
