"""Decoded peptide/clash barriers, distinct from reference-distance supervision."""
import torch
from torch.nn import functional as F
from .flow import target_noise


def local_geometry_loss(backbone, mask, config):
    if backbone.shape != (*mask.shape, 4, 3) or mask.dtype != torch.bool:
        raise ValueError('expected full backbone and bool residue mask')
    if not torch.isfinite(backbone).all() or not (mask.sum(1) >= 4).all():
        raise ValueError('invalid backbone')
    losses = []; components = []
    for bb, valid in zip(backbone, mask):
        # Require full contiguous proteins, never join over missing residues.
        n = int(valid.sum())
        if not valid[:n].all() or valid[n:].any(): raise ValueError('noncontiguous mask')
        bb = bb[:n]; ca = bb[:, 1]
        peptide = torch.linalg.vector_norm(bb[:-1, 2]-bb[1:, 0], dim=-1)
        adjacent = torch.linalg.vector_norm(ca[1:]-ca[:-1], dim=-1)
        i, j = torch.triu_indices(n, n, offset=3, device=bb.device)
        distance = torch.linalg.vector_norm(ca[i]-ca[j], dim=-1)
        values = torch.stack(((F.relu(config['peptide_interval'][0]-peptide).square()+F.relu(peptide-config['peptide_interval'][1]).square()).sum()/n, F.relu(config['clash_distance']-distance).square().sum()/n, F.relu(adjacent-config['maximum_ca_gap']).square().sum()/n))
        losses.append(values.sum()); components.append(values.detach())
    return torch.stack(losses).mean(), torch.stack(components).mean(0)


def endpoint_geometry(decoder, state, ids, lengths, config, step):
    eligible = torch.where((state['t'] >= config['minimum_time']) & ~state['dropped'])[0]
    generator = torch.Generator().manual_seed(config['noise_seed']+step)
    chosen = eligible[torch.randperm(len(eligible), generator=generator)[:config['maximum_examples']].to(eligible.device)]
    stats = dict(geometry_count=len(chosen), geometry_loss=0., peptide_loss=0., clash_loss=0., gap_loss=0.)
    if not len(chosen): return None, stats
    t = state['t'][chosen, None, None]
    z = F.layer_norm(state['x'][chosen]+(1-t)*state['velocity'][chosen], (8,)).float()
    positions = chosen.tolist()
    # Repeated training proteins can occur within a bucket batch. Slot suffixes
    # give independent deterministic decoder draws without consuming flow RNG.
    noise = target_noise([f'{ids[i]}:slot{i}' for i in positions], [4*lengths[i] for i in positions], 3, seed=config['noise_seed'], sample_index=step, stream='local_geometry_decoder', device=z.device)
    noise = F.pad(noise, (0, 0, 0, 4*z.shape[1]-noise.shape[1]))*decoder.fm.scale_ref
    _, bb = decoder(z, state['mask'][chosen], noise=noise, return_backbone=True)
    loss, values = local_geometry_loss(bb, state['mask'][chosen], config)
    if not torch.isfinite(loss): raise FloatingPointError('nonfinite local geometry loss')
    stats.update(geometry_loss=float(loss.detach()), peptide_loss=float(values[0]), clash_loss=float(values[1]), gap_loss=float(values[2]))
    return loss, stats
