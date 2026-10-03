"""Learned local latent inpainting with an immutable surrounding scaffold."""
import torch
from torch import nn
from torch.nn import functional as F
from .model import timestep_embedding
from .pair_model import PairDiTBlock
from .fragment_geometry_conditioning import FragmentGeometryAdapter


def editable_window(keep, mask, flank=8):
    if keep.dtype!=torch.bool or mask.dtype!=torch.bool or keep.shape!=mask.shape or (keep&~mask).any() or not keep.any(1).all() or flank<0:
        raise ValueError('Nonempty valid fragment masks required')
    return (F.max_pool1d(keep[:,None].float(),2*flank+1,stride=1,padding=flank)[:,0]>0)&mask


class MaskedFragmentFlow(nn.Module):
    def __init__(self,width=256,layers=4,heads=8,max_length=512):
        super().__init__();self.width=width
        self.input=nn.Linear(8,width);self.edit_embedding=nn.Embedding(2,width);self.position=nn.Embedding(max_length,width)
        self.time=nn.Sequential(nn.Linear(width,width),nn.SiLU(),nn.Linear(width,width))
        self.condition=FragmentGeometryAdapter(width,n_layers=layers,n_heads=heads,distance_precision='fp64')
        self.blocks=nn.ModuleList([PairDiTBlock(width,heads,32,0.,0) for _ in range(layers)])
        self.norm=nn.LayerNorm(width);self.output=nn.Linear(width,8)
        nn.init.zeros_(self.output.weight);nn.init.zeros_(self.output.bias)

    def prepare(self,features,keep,mask,coordinates,dropped):
        token=self.condition(features,keep,mask,dropped)
        pool=(token*keep[...,None]).sum(1)/keep.sum(1,keepdim=True)
        pair=self.condition.pair_biases(coordinates,keep,mask,dropped)
        return token,pool,pair

    def forward(self,x,t,mask,edit,prepared):
        token,pool,pair=prepared
        h=self.input(x)+self.edit_embedding(edit.long())+self.position.weight[:x.shape[1]][None]+token
        c=self.time(timestep_embedding(t,self.width))+pool
        for block,bias in zip(self.blocks,pair):h=block(h,c,mask,bias)
        return self.output(self.norm(h))*edit[...,None]


def masked_flow_loss(model,target,features,keep,mask,coordinates,*,generator,flank=8):
    edit=editable_window(keep,mask,flank)
    if target.shape!=(*mask.shape,8) or target.requires_grad or not torch.isfinite(target).all() or (target[~mask]!=0).any():raise ValueError('Finite fixed padded endpoints required')
    noise=torch.randn(target.shape,device=target.device,generator=generator)
    t=torch.sigmoid(torch.randn(len(target),device=target.device,generator=generator)).clamp(1e-4,1-1e-4)
    dropped=torch.rand(len(target),device=target.device,generator=generator)<.1
    x=torch.where(edit[...,None],(1-t[:,None,None])*noise+t[:,None,None]*target,target)
    prepared=model.prepare(features,keep,mask,coordinates,dropped)
    velocity=model(x,t,mask,edit,prepared)
    error=(velocity-(target-noise)).square().mean(-1)
    loss=((error*edit).sum(1)/edit.sum(1)).mean()
    return loss,dict(noise=noise,t=t,dropped=dropped,edit=edit)


@torch.no_grad()
def sample_masked_fragment(model,context,features,keep,mask,coordinates,*,noise,steps=20,flank=8,drop_fragment=False):
    if model.training or steps<1 or context.shape!=noise.shape or context.shape!=(*mask.shape,8) or not torch.isfinite(context).all() or not torch.isfinite(noise).all() or (context[~mask]!=0).any():raise ValueError('Eval model and finite padded context/noise required')
    edit=editable_window(keep,mask,flank)
    prepared=model.prepare(features,keep,mask,coordinates,torch.full((len(context),),drop_fragment,dtype=torch.bool,device=context.device))
    x=torch.where(edit[...,None],noise,context)
    for step in range(steps):
        t=x.new_full((len(x),),step/steps)
        x=torch.where(edit[...,None],x+model(x,t,mask,edit,prepared)/steps,context)
    result=torch.where(edit[...,None],F.layer_norm(x,(8,)),context)
    if not torch.isfinite(result).all() or not torch.equal(result[~edit],context[~edit]):raise ValueError('Invalid inpainting or changed fixed scaffold')
    return result
