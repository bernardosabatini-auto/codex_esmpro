"""Adapt a private pretrained decoder with explicit isolated-fragment denoising."""
import copy
from types import SimpleNamespace
import torch
from torch.utils.checkpoint import checkpoint
from .fragment_decoder import FragmentDecoder


class FragmentDenoisingDecoder(FragmentDecoder):
    def __init__(self, codec, **kwargs):
        # The trusted codec remains an independent historical-control model.
        local = SimpleNamespace(decoder=copy.deepcopy(codec.decoder), fm=codec.fm,
                                n_steps=codec.n_steps, target_pred=codec.target_pred)
        super().__init__(local, **kwargs)
        self.decoder.requires_grad_(True)

    def velocity(self, context, features, keep, mask, coordinates, x_t, t, dropped, *, checkpointed=True):
        if (mask.dtype != torch.bool or not mask.all() or context.shape != (*mask.shape, 8)
                or not torch.isfinite(context).all() or x_t.shape != (len(mask), 4*mask.shape[1], 3)
                or not torch.isfinite(x_t).all() or t.shape != (len(mask),)
                or not torch.isfinite(t).all() or (t < 0).any() or (t >= 1).any()):
            raise ValueError('Finite exact-length denoising inputs and times in [0,1) required')
        token, pair = self.adapter.prepare(features, keep, mask, coordinates, dropped)
        z = torch.where(keep[..., None], torch.zeros_like(context), context)
        atoms = mask.repeat_interleave(4, dim=1)
        def run(x, times, latent, token_delta, pair_delta):
            return self.decoder(dict(x_t=x, t=times, mask=mask, coords_mask=atoms, single_repr=latent,
                fragment_token_delta=token_delta, fragment_pair_delta=pair_delta))['coors_pred']
        args = (x_t, t, z, token, pair)
        return checkpoint(run, *args, use_reentrant=False) if checkpointed else run(*args)


def sample_times(batch, *, generator, device):
    # Beta(1.9,1) inverse CDF; original checkpoint uses 2% uniform mixture.
    u = torch.rand(3, batch, generator=generator, device=device)
    return torch.where(u[2] < .02, u[1], u[0].pow(1/1.9))


def denoising_inputs(target, noise, t):
    if (target.ndim != 4 or target.shape[2:] != (4,3) or target.requires_grad
            or noise.shape != (len(target), target.shape[1]*4,3)
            or not torch.isfinite(target).all() or not torch.isfinite(noise).all()):
        raise ValueError('Finite native backbone in Angstrom and explicit atom noise required')
    clean = target.flatten(1,2) / 10
    clean = clean - clean.mean(1,keepdim=True)
    initial = noise - noise.mean(1,keepdim=True)
    noisy = (1-t[:,None,None])*initial + t[:,None,None]*clean
    return clean, initial, noisy


def region_fm_loss(predicted_clean, clean, t, keep, *, motif_mass=.5):
    if not 0 < motif_mass < 1 or not keep.any(1).all() or keep.all(1).any():
        raise ValueError('Nonempty motif and scaffold required')
    error = (predicted_clean-clean).square().reshape(len(keep),keep.shape[1],4,3).mean((-1,-2))
    motif = (error*keep).sum(1)/keep.sum(1)
    scaffold = (error*~keep).sum(1)/(~keep).sum(1)
    weight = 1/((1-t).square()+1e-5)
    return ((motif_mass*motif+(1-motif_mass)*scaffold)*weight).mean(), dict(
        motif_fm=(motif*weight).mean().detach(), scaffold_fm=(scaffold*weight).mean().detach())


def fragment_denoising_loss(model, context, target, features, keep, mask, coordinates, *, noise, t, dropped, checkpointed=True):
    clean, _, noisy = denoising_inputs(target, noise, t)
    v = model.velocity(context,features,keep,mask,coordinates,noisy,t,dropped,checkpointed=checkpointed)
    predicted_clean = noisy+(1-t[:,None,None])*v
    loss, components = region_fm_loss(predicted_clean,clean,t,keep)
    if not torch.isfinite(loss): raise FloatingPointError('Nonfinite decoder flow-matching loss')
    return loss, components, predicted_clean
