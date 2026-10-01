"""Conditional flow targets for a finite, uniform empirical teacher ensemble."""
import torch


@torch.no_grad()
def empirical_velocity(selected, noise, times, bank, mask, valid):
    """Return posterior mean velocity and its per-coordinate variance.

    Shapes: selected/noise B,L,D; bank B,K,L,D; mask B,L; valid B,K.
    `selected` must be drawn uniformly from valid labels and `noise` from N(0,I).
    The posterior is conditional on x_t, time, and the protein identity. Averaging
    targets here preserves the expected squared-error gradient; it does not turn
    the endpoint distribution into a single mean structure. Add returned variance
    to squared residuals to recover the conditional expected original loss.

    Compute relative to the sampled label in float64 to avoid catastrophic
    cancellation when time is near one. Padding never enters the posterior.
    """
    if selected.ndim != 3 or noise.shape != selected.shape:
        raise ValueError('expected matching selected/noise B,L,D')
    b, length, width = selected.shape
    if (bank.ndim != 4 or bank.shape[0] != b or bank.shape[2:] != (length, width)
            or mask.shape != (b, length) or valid.shape != bank.shape[:2]
            or mask.dtype != torch.bool or valid.dtype != torch.bool
            or times.shape != (b,)):
        raise ValueError('incompatible empirical target shapes')
    tensors = (selected, noise, times, bank, mask, valid)
    if any(x.device != selected.device for x in tensors):
        raise ValueError('target tensors must share device')
    if any(x.requires_grad for x in tensors):
        raise ValueError('empirical targets must be fixed')
    if not mask.any(1).all() or not valid.any(1).all():
        raise ValueError('empty protein or teacher bank')
    if not ((times >= 0) & (times < 1)).all():
        raise ValueError('time must be in [0,1)')
    if not all(torch.isfinite(x).all() for x in (selected, noise, times, bank)):
        raise ValueError('nonfinite empirical targets')
    delta = (bank.double() - selected.double()[:, None]) * mask[:, None, :, None]
    if not ((delta.square().sum((2, 3)) == 0) & valid).any(1).all():
        raise ValueError('sampled label absent from valid bank')
    sigma = 1 - times.double()
    ratio = times.double() / sigma
    # Remove the common -||noise||^2/2 term from each log likelihood.
    logits = (ratio[:, None] * (noise.double()[:, None] * delta).sum((2, 3))
              - .5 * ratio[:, None].square() * delta.square().sum((2, 3)))
    prob = logits.masked_fill(~valid, -torch.inf).softmax(1)
    correction = (prob[:, :, None, None] * delta).sum(1)
    mean = selected.double() - noise.double() + correction / sigma[:, None, None]
    variance = (prob[:, :, None, None] *
                (delta - correction[:, None]).square()).sum(1) / sigma[:, None, None].square()
    return (mean * mask[:, :, None]).to(selected.dtype), variance.to(selected.dtype)
