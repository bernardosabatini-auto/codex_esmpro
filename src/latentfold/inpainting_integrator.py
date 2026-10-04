"""Fixed three-versus-ten step diagnostic for a frozen conditional decoder."""
import torch
from .fragment_inpainting import constrain_state,tangent_velocity


def decode_steps(model,context,features,keep,mask,coordinates,*,anchors,noise,steps):
    if steps not in (3,10):raise ValueError('Only declared resolutions3 and10 allowed')
    if anchors.shape!=(*mask.shape,4,3) or (anchors[~keep]!=0).any():raise ValueError('Sparse supplied anchors required')
    known=keep.repeat_interleave(4,1)
    fixed=torch.where(known[...,None],anchors.flatten(1,2)/10,torch.zeros_like(noise))
    x=constrain_state(noise,fixed,known);ts=torch.linspace(0,1,steps+1,device=x.device)
    dropped=torch.zeros(len(mask),dtype=torch.bool,device=mask.device)
    for k in range(steps):
        t=ts[k]*torch.ones(len(mask),device=x.device)
        v=model.velocity(context,features,keep,mask,coordinates,x,t,dropped,checkpointed=False)
        drift=tangent_velocity(v,known)*(1-ts[k])/(1-ts[k]+1e-6)
        x=constrain_state(x+drift*(ts[k+1]-ts[k]),fixed,known)
    return x.reshape(len(mask),mask.shape[1],4,3)*10
