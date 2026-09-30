"""Matched objectives: shared flow draws, independent geometry noise stream."""
import torch
from torch.nn import functional as F
from .flow import flow_loss, target_noise
from .geometry import revised_geometry
from .precision import inference_precision


def objective(model, decoder, batch, config, *, generator, geometry_weight=0.,
              geometry_seed=0, step=0, max_geometry=4, return_parts=False):
    if config.repeats != 1:
        raise ValueError('matched pilot uses distinct proteins, no repeat copies')
    flow, info = flow_loss(model,batch['z'],batch['esm'],batch['mask'],config,
                           generator=generator,return_state=geometry_weight>0,
                           residue_weights=batch.get('residue_weights'))
    stats=dict(flow_loss=float(flow.detach()), geometry_loss=0., geometry_count=0)
    if geometry_weight==0: return (flow, None, stats) if return_parts else (flow, stats)
    state=info['state']; eligible=torch.where((state['t']>=.75)&~state['dropped'])[0]
    # A separate CPU generator controls subset selection, leaving flow RNG intact.
    gen=torch.Generator().manual_seed(geometry_seed+step)
    index=eligible[torch.randperm(len(eligible),generator=gen)[:max_geometry].to(eligible.device)]
    if not len(index): return (flow, None, stats) if return_parts else (flow, stats)
    t=state['t'][index,None,None]
    z=F.layer_norm(state['x'][index]+(1-t)*state['velocity'][index],(8,)).float()
    mask=state['mask'][index]
    chosen=index.tolist(); ids=[batch['ids'][i] for i in chosen]
    lengths=[batch['lengths'][i] for i in chosen]
    noise=target_noise(ids,[4*n for n in lengths],3,seed=geometry_seed,
                       sample_index=step,stream='training_decoder',device=z.device)
    noise=F.pad(noise,(0,0,0,4*z.shape[1]-noise.shape[1]))
    # Disable outer mixed precision for the decoder and distance arithmetic.
    with inference_precision('fp32'):
        ca=decoder(z,mask,noise=noise)
        geometry,nlocal=revised_geometry(ca,batch['ca'][index],mask,batch['adjacent'][index])
    if not torch.isfinite(geometry): raise FloatingPointError('nonfinite geometry objective')
    stats.update(geometry_loss=float(geometry.detach()),geometry_count=len(chosen),local_quadruples=nlocal)
    return (flow, geometry, stats) if return_parts else (flow+geometry_weight*geometry, stats)


def controlled_backward(model, flow, geometry, *, weight, max_ratio=.1, loss_scale=128.):
    """Bound the auxiliary parameter gradient before merging into the flow gradient.

    No optimizer steps are skipped. A nonfinite gradient fails the run. This is
    an explicit gradient-combination rule, not a fixed scalar loss function.
    """
    parameters=[p for p in model.parameters() if p.requires_grad]
    gf=torch.autograd.grad(flow*loss_scale,parameters,retain_graph=geometry is not None,allow_unused=True)
    gf=[None if g is None else g.div_(loss_scale) for g in gf]
    def norm(grads):
        parts=[g.square().sum(dtype=torch.float64) for g in grads if g is not None]
        value=torch.stack(parts).sum().sqrt()
        if not torch.isfinite(value):raise FloatingPointError('nonfinite parameter gradient')
        return value
    nf=norm(gf)
    stats=dict(flow_parameter_grad_norm=float(nf),aux_parameter_grad_norm=0.,effective_geometry_weight=0.,aux_to_flow_ratio=0.)
    if geometry is not None:
        ga=torch.autograd.grad(geometry*loss_scale,parameters,allow_unused=True)
        ga=[None if g is None else g.div_(loss_scale) for g in ga]
        na=norm(ga)
        effective=min(weight,max_ratio*float(nf)/(float(na)+1e-30))
        stats.update(aux_parameter_grad_norm=float(na),effective_geometry_weight=effective,
                     aux_to_flow_ratio=effective*float(na)/(float(nf)+1e-30))
        left=[];right=[]
        for i,(f,g) in enumerate(zip(gf,ga)):
            if g is not None:
                if f is None:gf[i]=torch.zeros_like(g)
                left.append(gf[i]);right.append(g)
        torch._foreach_add_(left,right,alpha=effective)
    for parameter,gradient in zip(parameters,gf):parameter.grad=gradient
    return stats
