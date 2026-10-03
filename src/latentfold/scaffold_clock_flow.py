"""Whole-chain flow with explicit local noise clocks for fragment scaffolding.

The scaffold context is used only to initialize sampling. No native endpoint or
clean-context side channel enters the network. Velocity is parameterized against
local time; integration and endpoint self-conditioning include the clock rate.
"""
import torch
from torch import nn
from torch.nn import functional as F

from .checkpoints import load_legacy
from .fragment_cross_attention import load_fragment_adapter
from .fragment_conditioning import prepare_fragment_condition, fragment_velocity, region_balanced_loss
from .masked_fragment_flow import editable_window
from .unconditional_training import freeze_unused_conditioning, _detach


class ClockAdapter(nn.Module):
    def __init__(self, width, seed):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.hidden = nn.Linear(2, 256)
            self.output = nn.Linear(256, width)
            nn.init.zeros_(self.output.weight)
            nn.init.zeros_(self.output.bias)

    def forward(self, alpha, t):
        values = torch.stack((alpha, alpha * (1 - t[:, None])), -1)
        return self.output(F.silu(self.hidden(values))) * alpha[..., None]


def clock_offsets(keep, mask, scaffold_start, flank):
    if not isinstance(scaffold_start, (float, int)) or not 0 <= scaffold_start < 1:
        raise ValueError('Scaffold start must lie in [0,1)')
    window = editable_window(keep, mask, flank)
    return (~window & mask).float() * scaffold_start, window


class ScaffoldClockFlow(nn.Module):
    def __init__(self, net, fragment, seed):
        super().__init__()
        self.net, self.fragment = net, fragment
        self.clock = ClockAdapter(net.d_model, seed)
        self.frozen_names = ['net.' + k for k in freeze_unused_conditioning(net)]
        net.checkpoint_blocks = True

    def prepare(self, features, keep, mask, coordinates, dropped):
        return prepare_fragment_condition(self.net, self.fragment, features, keep, mask, dropped, coordinates=coordinates)

    def forward(self, x, t, mask, alpha, prepared, history=None):
        esm, base = prepared
        token = base[0] + self.clock(alpha, t)
        pool = (token * mask[..., None]).sum(1) / mask.sum(1, keepdim=True)
        condition = (token, pool, *base[2:])
        return fragment_velocity(self.net, self.fragment, x, t, esm, mask, x_sc=history, prepared=condition) * mask[..., None]


def load_scaffold_clock(checkpoint, seed):
    net, _ = load_legacy(checkpoint, trusted_pickle=True)
    ck = torch.load(checkpoint, map_location='cpu', weights_only=False, mmap=True)
    fragment = load_fragment_adapter(ck, net)
    if hasattr(fragment, 'cross_condition'):
        raise ValueError('Expected original geometry/token parent')
    return ScaffoldClockFlow(net, fragment, seed)


def scaffold_clock_loss(model, target, features, keep, mask, coordinates, *, generator,
                        scaffold_start=.5, de_novo_probability=.5, window_loss_mass=.5, flank=8):
    if (target.shape != (*mask.shape, 8) or target.requires_grad
            or not torch.isfinite(target).all() or (target[~mask] != 0).any()):
        raise ValueError('Fixed finite padded native endpoint required')
    if not 0 <= de_novo_probability <= 1:
        raise ValueError('Invalid de novo probability')
    alpha, window = clock_offsets(keep, mask, scaffold_start, flank)
    noise = torch.randn(target.shape, device=target.device, generator=generator)
    t = torch.sigmoid(torch.randn(len(target), device=target.device, generator=generator)).clamp(1e-4, 1-1e-4)
    dropped = torch.rand(len(target), device=target.device, generator=generator) < .1
    use_history = bool(torch.rand((), device=target.device, generator=generator) < .5)
    de_novo = torch.rand(len(target), device=target.device, generator=generator) < de_novo_probability
    alpha = alpha * (~de_novo)[:, None]
    local_t = alpha + (1 - alpha) * t[:, None]
    x = ((1 - local_t[..., None]) * noise + local_t[..., None] * target) * mask[..., None]
    prepared = model.prepare(features, keep, mask, coordinates, dropped)
    history = None
    if model.net.self_cond and use_history:
        with torch.no_grad():
            v = model(x, t, mask, alpha, _detach(prepared))
            history = (x + (1 - local_t[..., None]) * v) * mask[..., None]
    velocity = model(x, t, mask, alpha, prepared, history)
    error = (velocity - (target - noise)).square().mean(-1)
    loss = region_balanced_loss(error, window, mask, dropped, window_loss_mass)
    if not torch.isfinite(loss):
        raise FloatingPointError('Nonfinite scaffold-clock loss')
    return loss, dict(noise=noise, t=t, dropped=dropped, alpha=alpha, de_novo=de_novo,
                     window=window, self_conditioned=use_history)


@torch.no_grad()
def sample_scaffold_clock(model, context, features, keep, mask, coordinates, *, noise,
                          steps=50, scaffold_start=.5, flank=8, drop_fragment=False):
    if (model.training or type(steps) is not int or steps < 1 or context.shape != noise.shape
            or context.shape != (*mask.shape, 8) or not torch.isfinite(context).all()
            or not torch.isfinite(noise).all() or (context[~mask] != 0).any()):
        raise ValueError('Eval model and finite padded sampling inputs required')
    alpha, _ = clock_offsets(keep, mask, scaffold_start, flank)
    dropped = torch.full((len(context),), drop_fragment, dtype=torch.bool, device=context.device)
    prepared = model.prepare(features, keep, mask, coordinates, dropped)
    # Multiplication by alpha removes all endpoint information in the motif window.
    x = (alpha[..., None] * context + (1 - alpha[..., None]) * noise) * mask[..., None]
    history = None
    ts = torch.linspace(0, 1, steps + 1, device=x.device)
    for i in range(steps):
        t, dt = ts[i], ts[i + 1] - ts[i]
        velocity = model(x, t.expand(len(x)), mask, alpha, prepared, history).float()
        rate = (1 - alpha)[..., None]
        if model.net.self_cond:
            history = (x + (1 - t) * rate * velocity) * mask[..., None]
        x = (x + dt * rate * velocity) * mask[..., None]
    result = F.layer_norm(x, (8,)) * mask[..., None]
    if not torch.isfinite(result).all():
        raise FloatingPointError('Nonfinite scaffold-clock sample')
    return result
