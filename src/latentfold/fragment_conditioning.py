"""Explicit fragment inputs, distinct from output latents and scaffold sequence."""
import math
import torch
from torch import nn
from torch.nn import functional as F

AMINO_ACIDS = 'ACDEFGHIKLMNPQRSTVWY'
FEATURE_WIDTH = 29  # eight standalone latent channels, 20 supplied residues, mask


def fragment_features(latent, sequence, *, length, start):
    """Only cropped fragment codes/sequence enter; scaffold inputs are absent."""
    k = len(sequence)
    if latent.shape != (k, 8) or not torch.isfinite(latent).all():
        raise ValueError('Finite standalone fragment codes required')
    if k < 1 or start < 0 or start + k > length or any(a not in AMINO_ACIDS for a in sequence):
        raise ValueError('Invalid fragment placement or supplied residues')
    features = latent.new_zeros(length, FEATURE_WIDTH)
    keep = torch.zeros(length, dtype=torch.bool, device=latent.device)
    keep[start:start+k] = True
    features[keep, :8] = latent
    index = torch.tensor([AMINO_ACIDS.index(a) for a in sequence], device=latent.device)
    features[keep, 8:28] = F.one_hot(index, 20).to(latent.dtype)
    features[keep, 28] = 1
    return features, keep


class FragmentAdapter(nn.Module):
    def __init__(self, output_width, hidden=256):
        super().__init__()
        self.hidden = nn.Linear(FEATURE_WIDTH, hidden)
        self.output = nn.Linear(hidden, output_width)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    def forward(self, features, keep, mask, dropped):
        if features.shape != (*mask.shape, FEATURE_WIDTH) or keep.shape != mask.shape:
            raise ValueError('Invalid fragment feature shape')
        if keep.dtype != torch.bool or mask.dtype != torch.bool or dropped.shape != mask.shape[:1] or dropped.dtype != torch.bool:
            raise ValueError('Boolean fragment, padding and dropout masks required')
        if (keep & ~mask).any() or not keep.any(1).all() or not torch.isfinite(features).all():
            raise ValueError('Invalid fragment or padding')
        if (features[~keep] != 0).any() or not torch.equal(features[..., 28], keep.to(features.dtype)):
            raise ValueError('Scaffold features must be absent')
        delta = self.output(F.silu(self.hidden(features)))
        return delta * (keep & ~dropped[:, None])[..., None]


def prepare_fragment_condition(net, adapter, features, keep, mask, dropped, *, coordinates=None):
    """Reuse the pretrained learned-null condition; add fragment token features."""
    b, n = mask.shape
    # Preserve the established arithmetic initially; optimize only after parity.
    esm = features.new_zeros(b, n, net.cond_norm.normalized_shape[0])
    null = torch.ones(b, dtype=torch.bool, device=mask.device)
    kwargs = {}
    if hasattr(net, 'compute_pair'):
        kwargs['pair'] = features.new_zeros(b, n, n, net.null_pair.shape[-1])
    prepared = net.prepare_condition(esm, mask, null, **kwargs)
    token = prepared[0] + adapter(features, keep, mask, dropped)
    pool = (token * mask[..., None]).sum(1) / mask.sum(1, keepdim=True)
    if hasattr(adapter, 'pair_biases'):
        if coordinates is None or len(prepared)!=3:raise ValueError('Geometry conditioning requires supplied coordinates and pair-attention model')
        extra=adapter.pair_biases(coordinates,keep,mask,dropped)
        if len(extra)!=len(prepared[2]) or any(x.shape!=y.shape for x,y in zip(extra,prepared[2])):raise ValueError('Pair adapter architecture mismatch')
        return esm, (token,pool,tuple(x+y for x,y in zip(prepared[2],extra)))
    if coordinates is not None:raise ValueError('Token-only adapter does not consume coordinates')
    return esm, (token, pool, *prepared[2:])


def region_balanced_loss(error, keep, mask, dropped, motif_mass):
    """Fix the motif's loss mass while preserving uniform null-example loss."""
    if not math.isfinite(motif_mass) or not 0 < motif_mass < 1:
        raise ValueError('Motif loss mass must lie strictly between zero and one')
    motif = keep & mask
    scaffold = mask & ~keep
    nm, ns = motif.sum(1), scaffold.sum(1)
    if (mask.sum(1) == 0).any():
        raise ValueError('Empty training examples are invalid')
    active = ~dropped & (nm > 0) & (ns > 0)
    balanced = motif_mass * (error * motif).sum(1) / nm.clamp_min(1)
    balanced = balanced + (1 - motif_mass) * (error * scaffold).sum(1) / ns.clamp_min(1)
    uniform = (error * mask).sum(1) / mask.sum(1)
    return torch.where(active, balanced, uniform).mean()


def fragment_flow_loss(net, adapter, target, features, keep, mask, *, generator, coordinates=None, return_state=False, null_target=None, motif_weight=1., conditional_time_shift=0., motif_mass=None):
    """Protein-weighted flow matching; fragment dropout preserves a null branch."""
    if target.shape != (*mask.shape, 8) or target.requires_grad or not torch.isfinite(target).all():
        raise ValueError('Fixed finite full-structure latent targets required')
    if null_target is not None and (null_target.shape!=target.shape or null_target.requires_grad or not torch.isfinite(null_target).all()):raise ValueError('Fixed matching null targets required')
    if not math.isfinite(motif_weight) or motif_weight <= 0:
        raise ValueError('Finite positive motif weight required')
    if conditional_time_shift not in (0., -1.):
        raise ValueError('Only the declared zero or minus-one time shift is supported')
    b = len(target)
    noise = torch.randn(target.shape, device=target.device, generator=generator)
    t = torch.sigmoid(torch.randn(b, device=target.device, generator=generator)).clamp(1e-4, 1-1e-4)
    dropped = torch.rand(b, device=target.device, generator=generator) < .1
    use_history = bool(torch.rand((), device=target.device, generator=generator) < .5)
    base_t = t
    if conditional_time_shift:
        shifted = (t/(math.exp(-conditional_time_shift)*(1-t)+t)).clamp(1e-4, 1-1e-4)
        t = torch.where(~dropped & (keep & mask).any(1), shifted, t)
    if null_target is not None:target=torch.where(dropped[:,None,None],null_target,target)
    esm, prepared = prepare_fragment_condition(net, adapter, features, keep, mask, dropped, coordinates=coordinates)
    tt = t[:, None, None]
    x = (1-tt)*noise + tt*target
    history = None
    if net.self_cond and use_history:
        def detach(v):
            return v.detach() if isinstance(v, torch.Tensor) else tuple(detach(x) for x in v)
        with torch.no_grad():
            history = x + (1-tt)*net(x, t, esm, mask, x_sc=None, prepared=detach(prepared))
    velocity = net(x, t, esm, mask, x_sc=history, prepared=prepared)
    error = (velocity - (target-noise)).square().mean(-1)
    if motif_mass is not None:
        loss = region_balanced_loss(error, keep, mask, dropped, motif_mass)
    elif motif_weight == 1.:
        loss = ((error*mask).sum(1)/mask.sum(1)).mean()
    else:
        weights = mask * (1 + (motif_weight-1) * (keep & ~dropped[:, None]))
        loss = ((error*weights).sum(1)/weights.sum(1)).mean()
    if not torch.isfinite(loss):
        raise FloatingPointError('Nonfinite fragment flow loss')
    info=dict(noise=noise.detach(), t=t.detach(), dropped=dropped.detach(), self_conditioned=use_history)
    if conditional_time_shift:info['base_t']=base_t.detach()
    if null_target is not None:info['target']=target.detach()
    if return_state:info['state']=dict(x=x,velocity=velocity,t=t,dropped=dropped,mask=mask)
    return loss,info


@torch.no_grad()
def sample_fragment(net, adapter, features, keep, mask, *, noise, steps=50, drop_fragment=False, coordinates=None, guidance=1., reference=None, start_time=0.):
    if net.training or adapter.training or type(steps) is not int or steps < 1 or noise.shape != (*mask.shape, 8) or not torch.isfinite(noise).all():
        raise ValueError('Eval models and finite correctly shaped sampling noise required')
    if not isinstance(guidance,(int,float)) or not math.isfinite(guidance) or guidance<0:raise ValueError('Finite nonnegative guidance required')
    if not isinstance(start_time,(int,float)) or not math.isfinite(start_time) or not 0 <= start_time < 1:
        raise ValueError('Start time must lie in [0,1)')
    if reference is not None and (reference.shape != noise.shape or reference.device != noise.device or reference.dtype != noise.dtype or not torch.isfinite(reference).all()):
        raise ValueError('Finite matching reference codes required')
    if start_time and reference is None:
        raise ValueError('Partial flow requires reference codes')
    if guidance==0:drop_fragment=True
    dropped = torch.full((len(mask),), drop_fragment, dtype=torch.bool, device=mask.device)
    esm, prepared = prepare_fragment_condition(net, adapter, features, keep, mask, dropped, coordinates=coordinates)
    null_prepared=None
    if not drop_fragment and guidance!=1:
        _,null_prepared=prepare_fragment_condition(net,adapter,features,keep,mask,torch.ones_like(dropped),coordinates=coordinates)
    x = noise.clone() if start_time == 0 else start_time*reference + (1-start_time)*noise
    history = None
    ts = torch.linspace(start_time, 1, steps+1, device=noise.device)
    for i in range(steps):
        t, dt = ts[i], ts[i+1]-ts[i]
        v = net(x, t.expand(len(x)), esm, mask, x_sc=history, prepared=prepared).float()
        if null_prepared is not None:
            unconditional=net(x,t.expand(len(x)),esm,mask,x_sc=history,prepared=null_prepared).float();v=unconditional+guidance*(v-unconditional)
        if net.self_cond:
            history = x + (1-t)*v
        x = x + dt*v
    x = F.layer_norm(x, (8,))*mask[..., None]
    if not torch.isfinite(x).all():
        raise FloatingPointError('Nonfinite fragment sample')
    return x
