"""Coordinate bridge flow with distinct fragment and fixed-scaffold masks."""
import torch
from .fragment_inpainting import (FragmentInpaintingDecoder, context_mask, constrain_state,
                                  tangent_velocity, denoising_state)


def coordinate_known(keep, dropped, flank=8):
    if dropped.dtype!=torch.bool or dropped.shape!=(len(keep),):
        raise ValueError('One boolean fragment-dropout decision per protein required')
    hole=context_mask(keep,flank)
    known=~hole | (keep & ~dropped[:,None])
    if known.all(1).any():raise ValueError('Bridge requires unknown residues')
    return known


def scaffold_anchors(reference,motif_anchors,keep,flank=8):
    if (reference.shape!=(*keep.shape,4,3) or motif_anchors.shape!=reference.shape
            or not torch.isfinite(reference).all() or not torch.isfinite(motif_anchors).all()
            or (motif_anchors[~keep]!=0).any()):raise ValueError('Finite parent and isolated sparse motif anchors required')
    parent=reference-reference.mean((1,2),keepdim=True)
    far=~context_mask(keep,flank)
    return torch.where(far[...,None,None],parent,motif_anchors)


def bridge_weights(keep,dropped,*,flank=8,width=4,mass=.5):
    if not 0<width<flank or not 0<mass<1:raise ValueError('Interior bridge loss width/mass required')
    known=coordinate_known(keep,dropped,flank);unknown=~known
    near=(context_mask(keep,width)&~keep)&~dropped[:,None]
    rest=unknown&~near;nn,nr=near.sum(1)[:,None],rest.sum(1)[:,None]
    if (((nn==0)|(nr==0))&~dropped[:,None]).any():raise ValueError('Conditioned bridge needs both near and outer residues')
    weights=near*mass/nn.clamp_min(1)+rest*(1-mass)/nr.clamp_min(1)
    weights=torch.where(dropped[:,None],unknown/unknown.sum(1)[:,None],weights)
    return weights.repeat_interleave(4,1)/4


def bridge_loss(model,context,target,features,keep,mask,coordinates,*,noise,t,dropped,checkpointed=True,
                junction_width=4,junction_mass=.5):
    known_residues=coordinate_known(keep,dropped,model.context_flank)
    clean,noisy,anchors,known=denoising_state(target,noise,t,known_residues,torch.zeros_like(dropped))
    velocity=model.velocity(context,features,keep,mask,coordinates,noisy,t,dropped,checkpointed=checkpointed)
    predicted=constrain_state(noisy+(1-t[:,None,None])*tangent_velocity(velocity,known),anchors,known)
    weights=bridge_weights(keep,dropped,flank=model.context_flank,width=junction_width,mass=junction_mass)
    loss=(((predicted-clean).square().mean(-1)*weights).sum(1)/((1-t).square()+1e-5)).mean()
    if not torch.isfinite(loss):raise FloatingPointError('Nonfinite bridge flow loss')
    return loss,dict(unknown_fm=loss.detach()),predicted


class ScaffoldBridgeDecoder(FragmentInpaintingDecoder):
    def __init__(self,codec,*,context_flank=8,**kwargs):
        if context_flank!=8:raise ValueError('This prospective bridge uses exactly eight flanks')
        super().__init__(codec,context_flank=context_flank,**kwargs)
        self.state_audits=[]

    def forward(self,context,features,keep,mask,coordinates,*,anchors,noise,drop_fragment=False,checkpoint_steps=True):
        conditioned=coordinate_known(keep,torch.zeros(len(keep),dtype=torch.bool,device=keep.device),self.context_flank)
        if anchors.shape!=(*mask.shape,4,3) or not torch.isfinite(anchors).all() or (anchors[~conditioned]!=0).any():
            raise ValueError('Anchors may contain only motif and far-scaffold coordinates')
        dropped=torch.full((len(mask),),drop_fragment,dtype=torch.bool,device=mask.device)
        known=coordinate_known(keep,dropped,self.context_flank).repeat_interleave(4,1)
        fixed=torch.where(known[...,None],anchors.flatten(1,2)/10,torch.zeros_like(noise))
        x=constrain_state(noise,fixed,known);ts=torch.linspace(0,1,4,device=x.device)
        errors=[];centers=[]
        def check():
            errors.append(float((x[known]-fixed[known]).abs().max().detach()));centers.append(float(x.mean(1).abs().max().detach()))
            if errors[-1]>1e-5 or centers[-1]>1e-5:raise ValueError('Bridge anchors or affine center drifted')
        for step in range(3):
            check();t=ts[step]*torch.ones(len(mask),device=x.device)
            v=self.velocity(context,features,keep,mask,coordinates,x,t,dropped,
                            checkpointed=self.training and torch.is_grad_enabled() and checkpoint_steps)
            drift=tangent_velocity(v,known)*(1-ts[step])/(1-ts[step]+1e-6)
            x=constrain_state(x+drift*(ts[step+1]-ts[step]),fixed,known)
        check();self.state_audits.append(dict(known_max_abs_nm=max(errors),center_max_abs_nm=max(centers),states=len(errors),dropped=drop_fragment))
        return x.reshape(len(mask),mask.shape[1],4,3)*10
