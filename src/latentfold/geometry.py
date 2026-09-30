"""Differentiable, per-protein geometry terms with explicit correspondence.

Distances are in Angstroms. Adjacency must come from verified residue maps;
never infer it from array positions or a short coordinate distance alone.
"""
import torch
from torch.nn import functional as F


def _distances(pred, ref, mask):
    if pred.shape != ref.shape or pred.shape != (*mask.shape, 3) or mask.dtype != torch.bool:
        raise ValueError('expected matching (B,L,3) coordinates and boolean mask')
    if not torch.isfinite(pred).all() or not torch.isfinite(ref).all():
        raise ValueError('nonfinite coordinates')
    valid = mask[:, :, None] & mask[:, None, :]
    valid &= ~torch.eye(mask.shape[1], dtype=torch.bool, device=mask.device)[None]
    return torch.cdist(pred.float(), pred.float()), torch.cdist(ref.float(), ref.float()), valid


def _protein_mean(values, valid):
    count = valid.flatten(1).sum(1)
    if (count == 0).any():
        raise ValueError('no eligible residue pairs')
    return (values * valid).flatten(1).sum(1) / count


def legacy_lddt(pred, ref, mask):
    """Gate 19 formula, retained for diagnosis, including pooled pair weighting."""
    dp, dr, valid = _distances(pred, ref, mask)
    valid &= dr < 15
    if not valid.any():
        raise ValueError('no eligible local pairs')
    error = (dp-dr).abs()
    score = sum(torch.sigmoid(c-error) for c in (.5, 1., 2., 4.)) / 4
    return 1 - (score*valid).sum()/valid.sum()


def robust_distance(pred, ref, mask):
    """Equal local/global weights; Huber distance error divided by 10 Angstroms.

    Huber tails have nonzero constant slope, unlike sigmoid lDDT tails.
    Equal protein weighting prevents long proteins dominating the objective.
    """
    dp, dr, valid = _distances(pred, ref, mask)
    error = F.smooth_l1_loss(dp/10, dr/10, reduction='none', beta=.1)
    return (.5*_protein_mean(error, valid & (dr < 15)) + .5*_protein_mean(error, valid)).mean()


def signed_local(pred, ref, mask, adjacent):
    """Oriented CA quadruple volume / 3.8^3; sensitive to mirror inversion.

    Only three consecutive, explicitly mapped peptide adjacencies qualify.
    Returns zero and count zero when maps supply no eligible quadruples.
    """
    if adjacent.shape != (mask.shape[0], max(0, mask.shape[1]-1)) or adjacent.dtype != torch.bool:
        raise ValueError('explicit boolean residue adjacency required')
    if mask.shape[1] < 4:
        return pred.sum()*0, 0
    ok = adjacent[:, :-2] & adjacent[:, 1:-1] & adjacent[:, 2:]
    ok &= mask[:, :-3] & mask[:, 1:-2] & mask[:, 2:-1] & mask[:, 3:]
    def volume(x):
        d = x[:, 1:] - x[:, :-1]
        return (torch.linalg.cross(d[:, :-2], d[:, 1:-1], dim=-1)*d[:, 2:]).sum(-1)/(3.8**3)
    error = F.smooth_l1_loss(volume(pred), volume(ref), reduction='none', beta=.1)
    count = ok.sum(1)
    active = count > 0
    if not active.any():
        return pred.sum()*0, 0
    return ((error*ok).sum(1)[active]/count[active]).mean(), int(count.sum())


def revised_geometry(pred, ref, mask, adjacent):
    chirality, count = signed_local(pred, ref, mask, adjacent)
    return robust_distance(pred, ref, mask) + .1*chirality, count
