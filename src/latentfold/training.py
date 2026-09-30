"""Matched objectives: shared flow draws, independent geometry noise stream."""
import torch
from torch.nn import functional as F
from .flow import flow_loss, target_noise
from .geometry import revised_geometry
from .precision import inference_precision


def objective(model, decoder, batch, config, *, generator, geometry_weight=0.,
              geometry_seed=0, step=0, max_geometry=4):
    if config.repeats != 1:
        raise ValueError('matched pilot uses distinct proteins, no repeat copies')
    flow, info = flow_loss(model,batch['z'],batch['esm'],batch['mask'],config,
                           generator=generator,return_state=geometry_weight>0)
    stats=dict(flow_loss=float(flow.detach()), geometry_loss=0., geometry_count=0)
    if geometry_weight==0: return flow, stats
    state=info['state']; eligible=torch.where((state['t']>=.75)&~state['dropped'])[0]
    # A separate CPU generator controls subset selection, leaving flow RNG intact.
    gen=torch.Generator().manual_seed(geometry_seed+step)
    index=eligible[torch.randperm(len(eligible),generator=gen)[:max_geometry].to(eligible.device)]
    if not len(index): return flow, stats
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
    return flow+geometry_weight*geometry, stats
