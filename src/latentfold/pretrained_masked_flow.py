"""Local flow matching using the existing learned conditional latent prior."""
import torch
from torch import nn
from torch.nn import functional as F
from .checkpoints import load_legacy
from .fragment_cross_attention import load_fragment_adapter
from .fragment_conditioning import prepare_fragment_condition,fragment_velocity
from .masked_fragment_flow import editable_window
from .unconditional_training import freeze_unused_conditioning,_detach


class ScaffoldContext(nn.Module):
    def __init__(self,width,seed):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.hidden=nn.Linear(9,256);self.output=nn.Linear(256,width)
            nn.init.zeros_(self.output.weight);nn.init.zeros_(self.output.bias)

    def forward(self,context,known):
        # Mask BEFORE the network: editable native endpoints cannot leak.
        values=torch.cat((torch.where(known[...,None],context,torch.zeros_like(context)),known[...,None].to(context.dtype)),-1)
        return self.output(F.silu(self.hidden(values)))*known[...,None]


class PretrainedMaskedFlow(nn.Module):
    def __init__(self,net,fragment,seed):
        super().__init__();self.net=net;self.fragment=fragment;self.context=ScaffoldContext(net.d_model,seed)
        self.frozen_names=['net.'+k for k in freeze_unused_conditioning(net)]
        net.checkpoint_blocks=True

    def prepare(self,features,keep,mask,coordinates,dropped,context,edit):
        esm,base=prepare_fragment_condition(self.net,self.fragment,features,keep,mask,dropped,coordinates=coordinates)
        token=base[0]+self.context(context,mask&~edit);pool=(token*mask[...,None]).sum(1)/mask.sum(1,keepdim=True)
        return esm,(token,pool,*base[2:])

    def forward(self,x,t,mask,edit,prepared,history=None):
        esm,condition=prepared
        return fragment_velocity(self.net,self.fragment,x,t,esm,mask,x_sc=history,prepared=condition)*edit[...,None]


def load_pretrained(checkpoint,seed):
    net,_=load_legacy(checkpoint,trusted_pickle=True);ck=torch.load(checkpoint,map_location='cpu',weights_only=False,mmap=True)
    fragment=load_fragment_adapter(ck,net)
    if hasattr(fragment,'cross_condition'):raise ValueError('Expected unchanged geometry/token parent')
    return PretrainedMaskedFlow(net,fragment,seed)


def pretrained_masked_loss(model,target,features,keep,mask,coordinates,*,generator,flank=8):
    edit=editable_window(keep,mask,flank)
    if target.shape!=(*mask.shape,8) or target.requires_grad or not torch.isfinite(target).all() or (target[~mask]!=0).any():raise ValueError('Fixed finite padded native endpoint required')
    noise=torch.randn(target.shape,device=target.device,generator=generator);t=torch.sigmoid(torch.randn(len(target),device=target.device,generator=generator)).clamp(1e-4,1-1e-4)
    dropped=torch.rand(len(target),device=target.device,generator=generator)<.1;use_history=bool(torch.rand((),device=target.device,generator=generator)<.5)
    tt=t[:,None,None];x=torch.where(edit[...,None],(1-tt)*noise+tt*target,target)
    prepared=model.prepare(features,keep,mask,coordinates,dropped,target,edit);history=None
    if model.net.self_cond and use_history:
        with torch.no_grad():history=torch.where(edit[...,None],x+(1-tt)*model(x,t,mask,edit,_detach(prepared)),target)
    velocity=model(x,t,mask,edit,prepared,history);error=(velocity-(target-noise)).square().mean(-1)
    return ((error*edit).sum(1)/edit.sum(1)).mean(),dict(noise=noise,t=t,dropped=dropped,edit=edit,self_conditioned=use_history)


@torch.no_grad()
def sample_pretrained_masked(model,context,features,keep,mask,coordinates,*,noise,steps=50,flank=8,drop_fragment=False,edit_override=None):
    if model.training or steps<1 or context.shape!=noise.shape or context.shape!=(*mask.shape,8) or not torch.isfinite(context).all() or not torch.isfinite(noise).all() or (context[~mask]!=0).any():raise ValueError('Eval model and finite padded sampler inputs required')
    edit=editable_window(keep,mask,flank) if edit_override is None else edit_override
    if edit.shape!=mask.shape or edit.dtype!=torch.bool or (edit&~mask).any() or not edit.any(1).all():raise ValueError('Invalid editable region')
    dropped=torch.full((len(context),),drop_fragment,dtype=torch.bool,device=context.device);prepared=model.prepare(features,keep,mask,coordinates,dropped,context,edit)
    x=torch.where(edit[...,None],noise,context);history=None;ts=torch.linspace(0,1,steps+1,device=x.device)
    for step in range(steps):
        t,dt=ts[step],ts[step+1]-ts[step];velocity=model(x,t.expand(len(x)),mask,edit,prepared,history).float()
        if model.net.self_cond:history=torch.where(edit[...,None],x+(1-t)*velocity,context)
        x=torch.where(edit[...,None],x+dt*velocity,context)
    result=torch.where(edit[...,None],F.layer_norm(x,(8,)),context)
    if not torch.isfinite(result).all() or not torch.equal(result[~edit],context[~edit]):raise ValueError('Invalid repair or changed fixed scaffold')
    return result
