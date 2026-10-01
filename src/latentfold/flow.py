"""Explicit flow matching and sampling, independent of the old training framework."""
from dataclasses import dataclass
import hashlib
import math

import torch
from torch.nn import functional as F


@dataclass(frozen=True)
class FlowConfig:
    repeats: int = 1
    condition_dropout: float = 0.1
    self_condition_probability: float = 0.5
    time_mean: float = 0.0
    time_std: float = 1.0
    uniform_fraction: float = 0.0
    reduction: str = "protein"

    def __post_init__(self):
        if type(self.repeats) is not int or self.repeats < 1:
            raise ValueError("repeats must be a positive integer")
        for x in (self.condition_dropout, self.self_condition_probability, self.uniform_fraction):
            if not 0 <= x <= 1:
                raise ValueError("probabilities must be in [0, 1]")
        if not math.isfinite(self.time_mean) or not math.isfinite(self.time_std) or self.time_std <= 0:
            raise ValueError("invalid time distribution")
        if self.reduction not in ("protein", "residue"):
            raise ValueError("reduction must be protein or residue")


@dataclass(frozen=True)
class SampleConfig:
    steps: int = 25
    guidance: float = 2.0
    project: bool = True
    solver: str = 'euler'

    def __post_init__(self):
        if type(self.steps) is not int or self.steps < 1 or not math.isfinite(self.guidance):
            raise ValueError("invalid sampling settings")
        if self.solver not in ('euler','midpoint'):
            raise ValueError('unknown flow solver')


def validate_batch(esm, mask, z=None):
    if esm.ndim != 3 or mask.shape != esm.shape[:2] or mask.dtype != torch.bool:
        raise ValueError("expected embeddings (B,L,D) and bool mask (B,L)")
    if esm.shape[0] == 0 or not mask.any(1).all():
        raise ValueError("empty proteins are forbidden")
    if not torch.isfinite(esm).all():
        raise ValueError("nonfinite embeddings, including padding")
    if z is not None and (z.shape != (*mask.shape, 8) or not torch.isfinite(z).all()):
        raise ValueError("expected finite latents (B,L,8)")


def target_noise(ids, lengths, width, *, seed, sample_index=0, stream="flow", device="cpu"):
    """Stable noise per target, unaffected by batch size, ordering, or padding.

    Generate on CPU so the seed-to-noise mapping also survives changing device.
    Decoder uses a separate stream and lengths=4*residue_lengths, width=3.
    """
    if not ids or len(ids) != len(lengths) or len(set(ids)) != len(ids):
        raise ValueError("provide unique IDs and matching lengths")
    if any(type(n) is not int or n < 1 for n in lengths) or width < 1:
        raise ValueError("invalid noise shape")
    out = torch.zeros(len(ids), max(lengths), width)
    for i, (name, length) in enumerate(zip(ids, lengths)):
        payload = f"{seed}\0{sample_index}\0{stream}\0{name}".encode()
        local_seed = int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") % (2**63 - 1)
        gen = torch.Generator(device="cpu").manual_seed(local_seed)
        out[i, :length] = torch.randn(length, width, generator=gen)
    return out.to(device)


def flow_loss(net, z, esm, mask, config, *, generator, return_state=False, residue_weights=None, initial_noise=None, teacher_bank=None, teacher_valid=None):
    """One loss, with the effective sample count returned for logging.

    Protein weighting is the new default, matching the evaluation's unit of analysis.
    Set reduction='residue' to reproduce the legacy objective. This is an ablation,
    not an established accuracy improvement. Pair features are computed once.
    """
    validate_batch(esm, mask, z)
    if (teacher_bank is None) != (teacher_valid is None):
        raise ValueError('provide both empirical teacher bank and validity mask')
    if teacher_bank is not None:
        if initial_noise is not None:
            raise ValueError('empirical posterior requires independent Gaussian noise')
        teacher_bank = teacher_bank.repeat_interleave(config.repeats, 0)
        teacher_valid = teacher_valid.repeat_interleave(config.repeats, 0)
    if initial_noise is not None:
        if initial_noise.requires_grad or initial_noise.device != z.device or initial_noise.dtype != z.dtype:
            raise ValueError('paired noise must be fixed and match latent device/dtype')
        validate_batch(esm, mask, initial_noise)
        initial_noise = initial_noise.repeat_interleave(config.repeats, 0)
    if residue_weights is not None:
        if config.reduction != 'protein' or residue_weights.shape != mask.shape or residue_weights.requires_grad:
            raise ValueError('fixed residue weights require matching shape and protein reduction')
        if not torch.isfinite(residue_weights).all() or (residue_weights < 0).any() or not ((residue_weights*mask).sum(1) > 0).all():
            raise ValueError('invalid or empty residue confidence weights')
        residue_weights = residue_weights.repeat_interleave(config.repeats, 0)
    kwargs = {}
    if hasattr(net, "compute_pair"):
        kwargs["pair"] = net.compute_pair(esm, mask).repeat_interleave(config.repeats, 0)
    z, esm, mask = (x.repeat_interleave(config.repeats, 0) for x in (z, esm, mask))
    b = len(z)
    rnd = lambda shape: torch.rand(shape, device=z.device, generator=generator)
    x0 = torch.randn(z.shape, device=z.device, generator=generator)
    # Consume the same draw in paired and independent arms to preserve time/dropout RNG.
    if initial_noise is not None:
        x0 = initial_noise
    t = torch.sigmoid(config.time_mean + config.time_std * torch.randn(b, device=z.device, generator=generator))
    if config.uniform_fraction:
        t = torch.where(rnd((b,)) < config.uniform_fraction, rnd((b,)), t)
    t = t.clamp(1e-4, 1 - 1e-4)
    tt = t[:, None, None]
    x = (1 - tt) * x0 + tt * z
    drop = rnd((b,)) < config.condition_dropout
    sc = None
    if net.self_cond and rnd(()) < config.self_condition_probability:
        with torch.no_grad():
            v0 = net(x, t, esm, mask, drop, None, **{k: v.detach() for k, v in kwargs.items()})
            sc = (x + (1 - tt) * v0).detach()
    pred = net(x, t, esm, mask, drop, sc, **kwargs)
    if teacher_bank is None:
        errors = ((pred - (z - x0)) ** 2).mean(-1) * mask
    else:
        from .posterior_targets import empirical_velocity
        target, variance = empirical_velocity(z, x0, t, teacher_bank, mask, teacher_valid)
        errors = ((pred-target).square()+variance).mean(-1)*mask
    if residue_weights is not None:
        errors = errors * residue_weights
    if config.reduction == "protein":
        loss = (errors.sum(1) / mask.sum(1)).mean()
    else:
        loss = errors.sum() / mask.sum()
    if not torch.isfinite(loss):
        raise FloatingPointError("nonfinite flow loss")
    info = {"proteins": b // config.repeats, "noisy_copies": b, "repeats": config.repeats}
    if teacher_bank is not None:
        info['posterior_variance'] = (variance.mean(-1)*mask).sum(1)/mask.sum(1)
    if return_state:
        info["state"] = dict(velocity=pred, x=x, t=t, dropped=drop, mask=mask)
    return loss, info


@torch.no_grad()
def sample(net, esm, mask, config, *, noise, cache_condition=True, conditioning_ids=None):
    """Deterministic integration given explicit noise; no RNG inside.

    Midpoint uses two vector-field evaluations per interval. Self-conditioning
    advances at each evaluation, using its estimated endpoint. Formal second
    order accuracy only applies to an ordinary field without this learned
    history; actual checkpoints require empirical quality/validity controls.
    """
    validate_batch(esm, mask, noise)
    if net.training:
        raise ValueError("sampling requires net.eval()")
    if mask.shape[1] > net.pos.num_embeddings:
        raise ValueError("sequence exceeds checkpoint's position table")
    static_esm,static_mask,inverse=esm,mask,None
    if conditioning_ids is not None:
        if not cache_condition or len(conditioning_ids)!=len(esm):
            raise ValueError('conditioning reuse requires caching and one ID per prediction')
        groups={};first=[];mapping=[]
        for index,name in enumerate(conditioning_ids):
            if name not in groups:groups[name]=len(first);first.append(index)
            mapping.append(groups[name])
        first=torch.tensor(first,device=esm.device);inverse=torch.tensor(mapping,device=esm.device)
        static_esm=esm.index_select(0,first);static_mask=mask.index_select(0,first)
        if not torch.equal(esm,static_esm.index_select(0,inverse)) or not torch.equal(mask,static_mask.index_select(0,inverse)):
            raise ValueError('conditioning IDs merged different embeddings or masks')
    kwargs = {"pair": net.compute_pair(static_esm, static_mask)} if hasattr(net, "compute_pair") else {}
    x, sc = noise.clone(), None
    ts = torch.linspace(0, 1, config.steps + 1, device=esm.device)
    drop = torch.ones(len(esm), dtype=torch.bool, device=esm.device)
    cond_kwargs, uncond_kwargs = kwargs, kwargs
    if cache_condition:
        def expand(value):
            if inverse is None:return value
            if isinstance(value,torch.Tensor):return value.index_select(0,inverse)
            return tuple(expand(item) for item in value)
        cond_kwargs = {"prepared": expand(net.prepare_condition(static_esm, static_mask, **kwargs))}
        if config.guidance != 1:
            static_drop=torch.ones(len(static_esm),dtype=torch.bool,device=esm.device)
            uncond_kwargs = {"prepared": expand(net.prepare_condition(static_esm, static_mask, static_drop, **kwargs))}
        # Cached bias matrices replace the raw pair representation in the ODE loop.
        kwargs.clear()
    for i in range(config.steps):
        t = ts[i].expand(len(esm))
        v = net(x, t, esm, mask, None, sc, **cond_kwargs)
        if config.guidance != 1:
            uncond = net(x, t, esm, mask, drop, sc, **uncond_kwargs)
            v = uncond + config.guidance * (v - uncond)
        if config.solver == 'midpoint':
            dt=ts[i+1]-ts[i];middle=(ts[i]+ts[i+1])*.5
            middle_sc=x+(1-ts[i])*v if net.self_cond else None
            middle_x=x+.5*dt*v
            middle_t=middle.expand(len(esm))
            middle_v=net(middle_x,middle_t,esm,mask,None,middle_sc,**cond_kwargs)
            if config.guidance != 1:
                uncond=net(middle_x,middle_t,esm,mask,drop,middle_sc,**uncond_kwargs)
                middle_v=uncond+config.guidance*(middle_v-uncond)
            if net.self_cond:sc=middle_x+(1-middle)*middle_v
            x=x+dt*middle_v
            continue
        if net.self_cond:
            sc = x + (1 - ts[i]) * v
        x = x + v * (ts[i + 1] - ts[i])
    if config.project:
        x = F.layer_norm(x, (8,))
    if not torch.isfinite(x).all():
        raise FloatingPointError("nonfinite sampled latent")
    return x * mask.unsqueeze(-1)
