"""Fixed-resolution evaluation of the adapted decoder; no model updates."""
import torch


def decode_steps(model, context, features, keep, mask, coordinates, *, noise, steps, drop_fragment=False):
    if steps not in (3,10): raise ValueError('Only the declared three and ten step diagnostic is supported')
    if noise.shape!=(len(mask),4*mask.shape[1],3) or not torch.isfinite(noise).all():
        raise ValueError('Explicit finite atom noise required')
    x=noise.clone(); ts=torch.linspace(0,1,steps+1,device=x.device)
    dropped=torch.full((len(mask),),drop_fragment,dtype=torch.bool,device=x.device)
    atoms=mask.repeat_interleave(4,1)
    for k in range(steps):
        t=ts[k]*torch.ones(len(mask),device=x.device)
        velocity=model.velocity(context,features,keep,mask,coordinates,x,t,dropped,checkpointed=False)
        clean=x+(1-t[:,None,None])*velocity
        drift=(clean-x)/(1-ts[k]+1e-6)
        x=(x+drift*(ts[k+1]-ts[k]).item())*atoms[...,None].float()
    return x.reshape(len(mask),mask.shape[1],4,3)*10
