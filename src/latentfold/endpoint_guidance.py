"""Local latent corrections; preserving row statistics does not prove designability."""
import torch


def retract(proposal,reference):
    if proposal.shape!=reference.shape or proposal.ndim!=3 or proposal.shape[-1]!=8:raise ValueError('Matching latent arrays required')
    mu=reference.mean(-1,keepdim=True);radius=(reference-mu).norm(dim=-1,keepdim=True)
    center=proposal-proposal.mean(-1,keepdim=True);norm=center.norm(dim=-1,keepdim=True)
    if ((radius>1e-12)&(norm<=1e-12)).any():raise ValueError('Degenerate proposed latent direction')
    return torch.where(radius>1e-12,mu+center*(radius/norm.clamp_min(1e-12)),reference)


def tangent_gradient(gradient,point):
    g=gradient-gradient.mean(-1,keepdim=True);z=point-point.mean(-1,keepdim=True);norm=z.square().sum(-1,keepdim=True)
    tangent=g-z*(g*z).sum(-1,keepdim=True)/norm.clamp_min(1e-12)
    return torch.where(norm>1e-12,tangent,torch.zeros_like(tangent))


def proper_loss(backbone,fragment,start):
    """Half squared proper-rotation CA RMSD, with the optimal-rotation envelope gradient."""
    if backbone.ndim!=4 or backbone.shape[-2:]!=(4,3) or fragment.ndim!=3 or fragment.shape[1:]!=(4,3) or len(fragment)<3 or not 0<=start<=backbone.shape[1]-len(fragment):raise ValueError('Invalid motif placement')
    x=backbone[:,start:start+len(fragment),1].double();y=fragment[:,1].double();x=x-x.mean(1,keepdim=True);y=y-y.mean(0)
    with torch.no_grad():
        u,_,vt=torch.linalg.svd(x.transpose(1,2)@y);d=torch.eye(3,dtype=x.dtype,device=x.device)[None].repeat(len(x),1,1);d[:,-1,-1]=torch.linalg.det(u@vt);rotation=u@d@vt
    return .5*(x@rotation-y).square().sum(-1).mean(-1)
