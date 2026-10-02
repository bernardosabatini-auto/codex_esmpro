"""Explicit fragment inputs, distinct from output latents and scaffold sequence."""
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


def fragment_flow_loss(net, adapter, target, features, keep, mask, *, generator, coordinates=None):
    """Protein-weighted flow matching; fragment dropout preserves a null branch."""
    if target.shape != (*mask.shape, 8) or target.requires_grad or not torch.isfinite(target).all():
        raise ValueError('Fixed finite full-structure latent targets required')
    b = len(target)
    noise = torch.randn(target.shape, device=target.device, generator=generator)
    t = torch.sigmoid(torch.randn(b, device=target.device, generator=generator)).clamp(1e-4, 1-1e-4)
    dropped = torch.rand(b, device=target.device, generator=generator) < .1
    use_history = bool(torch.rand((), device=target.device, generator=generator) < .5)
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
    loss = (((velocity - (target-noise)).square().mean(-1)*mask).sum(1)/mask.sum(1)).mean()
    if not torch.isfinite(loss):
        raise FloatingPointError('Nonfinite fragment flow loss')
    return loss, dict(noise=noise.detach(), t=t.detach(), dropped=dropped.detach(), self_conditioned=use_history)


@torch.no_grad()
def sample_fragment(net, adapter, features, keep, mask, *, noise, steps=50, drop_fragment=False, coordinates=None):
    if net.training or adapter.training or type(steps) is not int or steps < 1 or noise.shape != (*mask.shape, 8) or not torch.isfinite(noise).all():
        raise ValueError('Eval models and finite correctly shaped sampling noise required')
    dropped = torch.full((len(mask),), drop_fragment, dtype=torch.bool, device=mask.device)
    esm, prepared = prepare_fragment_condition(net, adapter, features, keep, mask, dropped, coordinates=coordinates)
    x, history = noise.clone(), None
    ts = torch.linspace(0, 1, steps+1, device=noise.device)
    for i in range(steps):
        t, dt = ts[i], ts[i+1]-ts[i]
        v = net(x, t.expand(len(x)), esm, mask, x_sc=history, prepared=prepared).float()
        if net.self_cond:
            history = x + (1-t)*v
        x = x + dt*v
    x = F.layer_norm(x, (8,))*mask[..., None]
    if not torch.isfinite(x).all():
        raise FloatingPointError('Nonfinite fragment sample')
    return x
