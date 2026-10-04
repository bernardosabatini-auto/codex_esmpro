"""Explicit isolated-fragment conditioning inside the frozen coordinate decoder.

Only new token and pair residuals are trained. External ProteinAE source and
weights remain unchanged. No native motif endpoint is visible in masked codes.
"""
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint

from .fragment_conditioning import FragmentAdapter


class DecoderFragmentAdapter(FragmentAdapter):
    def __init__(self, token_width=256, pair_width=128, seed=2026100481):
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            super().__init__(token_width, hidden=256)
            self.pair_hidden = nn.Linear(17, 64)
            self.pair_output = nn.Linear(64, pair_width)
            nn.init.zeros_(self.pair_output.weight)
            nn.init.zeros_(self.pair_output.bias)
        self.register_buffer('centers', torch.arange(0, 32, 2, dtype=torch.float32))

    def prepare(self, features, keep, mask, coordinates, dropped):
        token = super().forward(features, keep, mask, dropped)
        if (coordinates.shape != (*mask.shape, 3) or not torch.isfinite(coordinates).all()
                or (coordinates[~keep] != 0).any()):
            raise ValueError('Only finite supplied fragment coordinates are allowed')
        distance = torch.cdist(coordinates.double(), coordinates.double(), compute_mode='donot_use_mm_for_euclid_dist').float()
        rbf = torch.exp(-.5 * ((distance[..., None] - self.centers) / 2).square())
        values = torch.cat((rbf, (distance / (distance + 10))[..., None]), -1)
        known = keep[:, :, None] & keep[:, None, :] & ~dropped[:, None, None]
        pair = self.pair_output(F.silu(self.pair_hidden(values))) * known[..., None]
        return token, pair


class FeatureResidual(nn.Module):
    """Add an explicitly supplied residual to a frozen batch-feature module."""
    def __init__(self, base, key):
        super().__init__()
        self.base, self.key = base, key

    def forward(self, batch):
        original = self.base(batch)
        delta = batch.get(self.key)
        if delta is None:
            return original
        if delta.shape != original.shape or delta.dtype != original.dtype:
            raise ValueError('Decoder feature residual shape or precision changed')
        return original + delta


class FragmentDecoder(nn.Module):
    def __init__(self, codec, *, seed=2026100481, token_width=256, pair_width=128):
        super().__init__()
        if codec.n_steps != 3 or codec.target_pred != 'v':
            raise ValueError('The established three-step velocity decoder is required')
        self.decoder = codec.decoder
        if isinstance(self.decoder.cond_factory, FeatureResidual) or isinstance(self.decoder.pair_repr_builder, FeatureResidual):
            raise ValueError('Decoder already has fragment adapters')
        self.decoder.requires_grad_(False)
        self.decoder.cond_factory = FeatureResidual(self.decoder.cond_factory, 'fragment_token_delta')
        self.decoder.pair_repr_builder = FeatureResidual(self.decoder.pair_repr_builder, 'fragment_pair_delta')
        self.adapter = DecoderFragmentAdapter(token_width, pair_width, seed)
        self.scale_ref = float(codec.fm.scale_ref)
        self.n_steps = 3
        self.train(False)

    def train(self, mode=True):
        super().train(mode)
        self.decoder.eval()
        self.adapter.train(mode)
        return self

    def forward(self, context, features, keep, mask, coordinates, *, noise,
                drop_fragment=False, mask_fragment=True, checkpoint_steps=True):
        if (mask.dtype != torch.bool or not mask.all() or context.shape != (*mask.shape, 8)
                or not torch.isfinite(context).all() or noise.shape != (len(mask), 4 * mask.shape[1], 3)
                or not torch.isfinite(noise).all()):
            raise ValueError('Finite exact-length decoder batches and explicit atom noise required')
        dropped = torch.full((len(mask),), drop_fragment, dtype=torch.bool, device=mask.device)
        token, pair = self.adapter.prepare(features, keep, mask, coordinates, dropped)
        z = torch.where(keep[..., None], torch.zeros_like(context), context) if mask_fragment else context
        atoms = mask.repeat_interleave(4, dim=1)

        def run(x, t, latent, token_delta, pair_delta):
            return self.decoder(dict(x_t=x, t=t, mask=mask, coords_mask=atoms, single_repr=latent,
                                     fragment_token_delta=token_delta, fragment_pair_delta=pair_delta))['coors_pred']

        x = noise.clone()
        ts = torch.linspace(0, 1, 4, device=x.device)
        for step in range(3):
            t = ts[step] * torch.ones(len(mask), device=x.device)
            if self.training and torch.is_grad_enabled() and checkpoint_steps:
                velocity = checkpoint(run, x, t, z, token, pair, use_reentrant=False)
            else:
                velocity = run(x, t, z, token, pair)
            clean = x + (1 - t[:, None, None]) * velocity
            v = (clean - x) / (1 - ts[step] + 1e-6)
            x = (x + v * (ts[step + 1] - ts[step]).item()) * atoms[..., None].float()
        bb = x.reshape(len(mask), mask.shape[1], 4, 3) * 10
        if not torch.isfinite(bb).all():
            raise FloatingPointError('Nonfinite conditioned decoder output')
        return bb

    def frozen_state(self):
        return self.decoder.state_dict()


def weighted_backbone_mse(predicted, target, keep, motif_mass=.5):
    """Proper weighted Procrustes loss, envelope gradient, Angstrom squared."""
    if (predicted.shape != target.shape or predicted.shape != (*keep.shape, 4, 3)
            or keep.dtype != torch.bool or not keep.any(1).all() or keep.all(1).any()
            or target.requires_grad or not torch.isfinite(target).all() or not torch.isfinite(predicted).all()
            or not 0 < motif_mass < 1):
        raise ValueError('Finite complete backbones and a nonempty proper motif required')
    weights = motif_mass * keep / keep.sum(1, keepdim=True)
    weights = weights + (1 - motif_mass) * (~keep) / (~keep).sum(1, keepdim=True)
    w = (weights[..., None].expand(-1, -1, 4) / 4).reshape(len(keep), -1)
    p, q = predicted.flatten(1, 2), target.flatten(1, 2)
    p = p - (p * w[..., None]).sum(1, keepdim=True)
    q = q - (q * w[..., None]).sum(1, keepdim=True)
    with torch.no_grad():
        u, _, vh = torch.linalg.svd((p.detach().double() * w[..., None].double()).transpose(1, 2) @ q.double())
        sign = torch.ones(len(keep), 3, dtype=torch.float64, device=p.device)
        sign[:, -1] = torch.where(torch.linalg.det(u @ vh) < 0, -1., 1.)
        rotation = ((u * sign[:, None]) @ vh).to(p)
    return (((p @ rotation - q).square().sum(-1) * w).sum(1)).mean()


def backbone_bond_mse(predicted, target):
    """Match native N-CA, CA-C, C-O and inter-residue C-N lengths."""
    def lengths(bb):
        local = (bb[:, :, [0, 1, 2]] - bb[:, :, [1, 2, 3]]).norm(dim=-1).flatten(1)
        peptide = (bb[:, :-1, 2] - bb[:, 1:, 0]).norm(dim=-1)
        return torch.cat((local, peptide), 1)
    return (lengths(predicted) - lengths(target)).square().mean()


def fragment_decoder_loss(model, context, target, features, keep, mask, coordinates, *, noise):
    predicted = model(context, features, keep, mask, coordinates, noise=noise)
    position = weighted_backbone_mse(predicted, target, keep)
    bonds = backbone_bond_mse(predicted, target)
    loss = position + bonds
    if not torch.isfinite(loss):
        raise FloatingPointError('Nonfinite decoder training objective')
    return loss, dict(position_mse=position.detach(), bond_mse=bonds.detach())
