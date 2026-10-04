"""Conditional coordinate flow in an affine space with fixed motif atoms.

Coordinates in the flow are nm. Placement inputs/outputs are Angstroms.
Unknown coordinates conserve the full-chain center without moving anchors.
"""
import torch
from .fragment_decoder_fm import FragmentDenoisingDecoder


def place_fragment(fragment, reference, start):
    """Place only the supplied fragment in a generated reference's frame."""
    if (reference.ndim != 4 or reference.shape[2:] != (4, 3)
            or fragment.ndim != 3 or fragment.shape[1:] != (4, 3)
            or len(fragment) < 3 or start < 0 or start+len(fragment) > reference.shape[1]
            or not torch.isfinite(reference).all() or not torch.isfinite(fragment).all()):
        raise ValueError('Finite full-atom reference and isolated fragment required')
    ref = reference.double()
    ref = ref-ref.mean((1, 2), keepdim=True)
    moving = fragment.double().flatten(0, 1)
    moving = moving-moving.mean(0)
    fixed = ref[:, start:start+len(fragment)].flatten(1, 2)
    center = fixed.mean(1, keepdim=True)
    u, singular, vh = torch.linalg.svd(moving.T @ (fixed-center))
    if (singular[:, -1] <= 1e-8*singular[:, 0]).any():
        raise ValueError('Degenerate fragment placement')
    signs = torch.ones_like(singular)
    signs[:, -1] = torch.where(torch.linalg.det(u @ vh) < 0, -1., 1.)
    rotation = (u*signs[:, None]) @ vh
    placed = (moving @ rotation+center).reshape(len(ref), len(fragment), 4, 3)
    result = reference.new_zeros(reference.shape)
    result[:, start:start+len(fragment)] = placed.to(reference)
    return result


def _check(x, anchors, known):
    if (x.ndim != 3 or x.shape[-1] != 3 or anchors.shape != x.shape
            or known.shape != x.shape[:2] or known.dtype != torch.bool
            or known.all(1).any() or not torch.isfinite(x).all()
            or not torch.isfinite(anchors).all() or (anchors[~known] != 0).any()):
        raise ValueError('Finite atom arrays, sparse anchors and unknown atoms required')


def constrain_state(x, anchors, known):
    _check(x, anchors, known)
    unknown = ~known
    y = torch.where(known[..., None], anchors, x)
    shift = y.sum(1, keepdim=True)/unknown.sum(1)[:, None, None]
    return torch.where(known[..., None], anchors, y-shift)


def tangent_velocity(v, known):
    return constrain_state(v, torch.zeros_like(v), known)


def denoising_state(target, noise, t, keep, dropped):
    if (target.shape != (*keep.shape, 4, 3) or target.requires_grad
            or not torch.isfinite(target).all() or noise.shape != (len(keep), 4*keep.shape[1], 3)
            or keep.dtype != torch.bool or dropped.dtype != torch.bool
            or dropped.shape != (len(keep),) or t.shape != (len(keep),)
            or not torch.isfinite(t).all() or (t < 0).any() or (t >= 1).any()):
        raise ValueError('Finite detached target, exact masks and valid times required')
    clean = target.flatten(1, 2)/10
    clean = clean-clean.mean(1, keepdim=True)
    known = (keep & ~dropped[:, None]).repeat_interleave(4, 1)
    anchors = torch.where(known[..., None], clean, torch.zeros_like(clean))
    initial = constrain_state(noise, anchors, known)
    noisy = constrain_state((1-t[:, None, None])*initial+t[:, None, None]*clean, anchors, known)
    return clean, noisy, anchors, known


def junction_atom_weights(keep, dropped, *, width, mass):
    """Unit loss mass per example; emphasize unknown flanks, never anchors.

    Dropout restores uniform mass across every atom. Exact-length batches only.
    """
    if (keep.ndim != 2 or keep.dtype != torch.bool or dropped.shape != (len(keep),)
            or dropped.dtype != torch.bool or not isinstance(width, int) or width < 1
            or not 0 < mass < 1 or not keep.any(1).all()):
        raise ValueError('Contained contiguous motifs, positive width and interior mass required')
    positions = torch.arange(keep.shape[1], device=keep.device)[None]
    start = torch.where(keep, positions, keep.shape[1]).amin(1)[:, None]
    end = torch.where(keep, positions, -1).amax(1)[:, None]+1
    if not torch.equal(keep, (positions >= start) & (positions < end)):
        raise ValueError('A single contiguous motif is required')
    flank = (((positions >= start-width) & (positions < start)) |
             ((positions >= end) & (positions < end+width))) & ~dropped[:, None]
    unknown = ~(keep & ~dropped[:, None])
    rest = unknown & ~flank
    nf, nr = flank.sum(1)[:, None], rest.sum(1)[:, None]
    if (((nf == 0) | (nr == 0)) & ~dropped[:, None]).any():
        raise ValueError('Conditioned examples need flank and remaining scaffold atoms')
    weights = flank*mass/nf.clamp_min(1) + rest*(1-mass)/nr.clamp_min(1)
    weights = torch.where(dropped[:, None], unknown/unknown.sum(1)[:, None], weights)
    return weights.repeat_interleave(4, 1)/4


def inpainting_loss(model, context, target, features, keep, mask, coordinates, *, noise, t, dropped, checkpointed=True,
                    junction_width=None, junction_mass=None):
    clean, noisy, anchors, known = denoising_state(target, noise, t, keep, dropped)
    velocity = model.velocity(context, features, keep, mask, coordinates, noisy, t, dropped, checkpointed=checkpointed)
    predicted = constrain_state(noisy+(1-t[:, None, None])*tangent_velocity(velocity, known), anchors, known)
    error = (predicted-clean).square().mean(-1)
    if junction_width is None and junction_mass is None:
        per_example = (error*~known).sum(1)/(~known).sum(1)/((1-t).square()+1e-5)
    else:
        if not mask.all():
            raise ValueError('Junction weighting requires exact-length batches')
        weights = junction_atom_weights(keep, dropped, width=junction_width, mass=junction_mass)
        per_example = (error*weights).sum(1)/((1-t).square()+1e-5)
    loss = per_example.mean()
    if not torch.isfinite(loss):
        raise FloatingPointError('Nonfinite inpainting loss')
    return loss, dict(unknown_fm=loss.detach()), predicted


def context_mask(keep, flank=0):
    """Hide nearby latent context without changing the fixed-coordinate mask."""
    if keep.ndim != 2 or keep.dtype != torch.bool or type(flank) is not int or flank < 0 or not keep.any(1).all():
        raise ValueError('Nonempty boolean fragment masks and nonnegative integer flank required')
    if flank == 0:
        return keep
    positions = torch.arange(keep.shape[1], device=keep.device)[None]
    start = torch.where(keep, positions, keep.shape[1]).amin(1)[:, None]
    end = torch.where(keep, positions, -1).amax(1)[:, None] + 1
    if not torch.equal(keep, (positions >= start) & (positions < end)):
        raise ValueError('Context flanks require a single contiguous motif')
    return (positions >= start-flank) & (positions < end+flank)


class FragmentInpaintingDecoder(FragmentDenoisingDecoder):
    def __init__(self, codec, *, context_flank=0, **kwargs):
        if type(context_flank) is not int or context_flank < 0:
            raise ValueError('Nonnegative integer context flank required')
        super().__init__(codec, **kwargs)
        self.context_flank = context_flank

    def velocity(self, context, features, keep, mask, coordinates, x_t, t, dropped, *, checkpointed=True):
        if self.context_flank:
            hidden = context_mask(keep, self.context_flank)
            context = torch.where(hidden[..., None], torch.zeros_like(context), context)
        return super().velocity(context, features, keep, mask, coordinates, x_t, t, dropped, checkpointed=checkpointed)

    def forward(self, context, features, keep, mask, coordinates, *, anchors, noise,
                drop_fragment=False, checkpoint_steps=True):
        if anchors.shape != (*mask.shape, 4, 3):
            raise ValueError('Sparse full-atom anchors in Angstrom required')
        if (anchors[~keep] != 0).any() or not torch.isfinite(anchors).all():
            raise ValueError('Anchors must contain only supplied fragment atoms')
        dropped = torch.full((len(mask),), drop_fragment, dtype=torch.bool, device=mask.device)
        known = (keep & ~dropped[:, None]).repeat_interleave(4, 1)
        fixed = torch.where(known[..., None], anchors.flatten(1, 2)/10, torch.zeros_like(noise))
        x = constrain_state(noise, fixed, known)
        ts = torch.linspace(0, 1, 4, device=x.device)
        for step in range(3):
            t = ts[step]*torch.ones(len(mask), device=x.device)
            v = self.velocity(context, features, keep, mask, coordinates, x, t, dropped,
                              checkpointed=self.training and torch.is_grad_enabled() and checkpoint_steps)
            # Keep the original decoder's Euler denominator convention.
            drift = tangent_velocity(v, known)*(1-ts[step])/(1-ts[step]+1e-6)
            x = constrain_state(x+drift*(ts[step+1]-ts[step]), fixed, known)
        return x.reshape(len(mask), mask.shape[1], 4, 3)*10
