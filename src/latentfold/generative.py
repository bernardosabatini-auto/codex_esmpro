"""Unconditional Euler sampling with explicit, reproducible motif resampling.

Ports the original motif recipe without importing side-effectful gate scripts.
Callers provide motif codes and record whether they came from a complete
structure or an isolated fragment; this sampler does not encode coordinates.
"""
import torch
from torch.nn import functional as F
from .flow import validate_batch


@torch.no_grad()
def sample_unconditional(net, esm, mask, *, noise, steps, fixed=None,
                         motif_noise=None, repaint=1, fresh_noise=None, update_history_each_eval=False):
    validate_batch(esm, mask, noise)
    if type(update_history_each_eval) is not bool:raise ValueError('history update flag must be boolean')
    if net.training or type(steps) is not int or steps < 1 or type(repaint) is not int or repaint < 1:
        raise ValueError('eval model and positive integer steps/refinements required')
    if mask.shape[1] > net.pos.num_embeddings:
        raise ValueError('sequence exceeds position table')
    if fixed is None and (repaint != 1 or motif_noise is not None):
        raise ValueError('motif arguments require fixed codes')
    if fixed is not None:
        target, keep = fixed
        validate_batch(esm, mask, target)
        validate_batch(esm, mask, motif_noise)
        if keep.dtype != torch.bool or keep.shape != mask.shape or (keep & ~mask).any() or not keep.any(1).all():
            raise ValueError('invalid motif mask')
        if repaint > 1 and fresh_noise is None:
            raise ValueError('explicit refinement noise required')
    drop = torch.ones(len(esm), dtype=torch.bool, device=esm.device)
    # Every token and pair is replaced by learned null conditioning. Passing a
    # zero pair skips unused sequence-conditioned pair computation, checked
    # against the generic CFG=0 sampler in both CPU and actual-checkpoint tests.
    kwargs = {}
    if hasattr(net, 'compute_pair'):
        kwargs['pair'] = net.null_pair.new_zeros(len(esm), mask.shape[1], mask.shape[1], net.null_pair.shape[-1])
    prepared = net.prepare_condition(torch.zeros_like(esm), mask, drop, **kwargs)
    x, sc = noise.clone(), None
    ts = torch.linspace(0, 1, steps + 1, device=esm.device)
    for i in range(steps):
        t, dt = ts[i], ts[i+1] - ts[i]
        if fixed is not None:
            x = torch.where(keep[..., None], (1-t)*motif_noise + t*target, x)
        v = net(x, t.expand(len(x)), esm, mask, drop, sc, prepared=prepared).float()
        if net.self_cond:
            sc = x + (1-t)*v
        x = x + dt*v
        if fixed is not None and i < steps-1:
            for j in range(repaint-1):
                eps = fresh_noise(i, j)
                validate_batch(esm, mask, eps)
                endpoint = x + (1-ts[i+1])*v
                x = (1-t)*eps + t*endpoint
                x = torch.where(keep[..., None], (1-t)*motif_noise + t*target, x)
                # Default preserves the source recipe. The explicit ablation
                # refreshes history after each inner evaluation as well.
                v = net(x, t.expand(len(x)), esm, mask, drop, sc, prepared=prepared).float()
                if update_history_each_eval and net.self_cond:
                    sc = x + (1-t)*v
                x = x + dt*v
    x = F.layer_norm(x, (8,))*mask[..., None]
    if not torch.isfinite(x).all():
        raise FloatingPointError('nonfinite generated latent')
    return x
