"""Explicit null-conditioned flow loss for matched trajectory compression."""
import torch

UNUSED_PREFIXES=('pair.','cond_norm.','cond_proj.')


def freeze_unused_conditioning(net):
    frozen=[]
    for name,p in net.named_parameters():
        if name.startswith(UNUSED_PREFIXES):p.requires_grad_(False);frozen.append(name)
    return frozen


def _detach(value):
    return value.detach() if isinstance(value,torch.Tensor) else tuple(_detach(v) for v in value)


def unconditional_loss(net, endpoint, mask, *, recorded_noise, paired, generator):
    if endpoint.shape!=recorded_noise.shape or endpoint.shape!=(*mask.shape,8) or mask.dtype!=torch.bool or endpoint.requires_grad or recorded_noise.requires_grad:
        raise ValueError('Fixed matching endpoint/noise tensors and boolean mask required')
    if not mask.any(1).all() or not torch.isfinite(endpoint).all() or not torch.isfinite(recorded_noise).all():raise ValueError('Invalid training targets')
    b,n=mask.shape
    # Both arms consume identical RNG even when the independent draw is unused.
    independent=torch.randn(endpoint.shape,device=endpoint.device,generator=generator)
    x0=recorded_noise if paired else independent
    t=torch.sigmoid(torch.randn(b,device=endpoint.device,generator=generator))
    choice=torch.rand(b,device=endpoint.device,generator=generator)<.5
    uniform=torch.rand(b,device=endpoint.device,generator=generator)
    t=torch.where(choice,uniform,t).clamp(1e-4,1-1e-4);tt=t[:,None,None]
    x=(1-tt)*x0+tt*endpoint
    esm=endpoint.new_zeros(b,n,net.cond_norm.normalized_shape[0]);drop=torch.ones(b,dtype=torch.bool,device=endpoint.device)
    kwargs={}
    if hasattr(net,'compute_pair'):kwargs['pair']=endpoint.new_zeros(b,n,n,net.null_pair.shape[-1])
    prepared=net.prepare_condition(esm,mask,drop,**kwargs)
    sc=None;use_sc=bool(torch.rand((),device=endpoint.device,generator=generator)<.5)
    if net.self_cond and use_sc:
        with torch.no_grad():sc=x+(1-tt)*net(x,t,esm,mask,drop,None,prepared=_detach(prepared))
    v=net(x,t,esm,mask,drop,sc,prepared=prepared)
    loss=(((v-(endpoint-x0)).square().mean(-1)*mask).sum(1)/mask.sum(1)).mean()
    if not torch.isfinite(loss):raise FloatingPointError('Nonfinite unconditional loss')
    return loss,dict(t=t.detach(),self_conditioned=use_sc)
