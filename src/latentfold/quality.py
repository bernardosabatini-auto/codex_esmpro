"""Fixed training-reference confidence weights; no predictions enter this rule."""
import torch


def confidence_weights(plddt, normalization=1.):
    if not torch.isfinite(plddt).all() or ((plddt < 0) | (plddt > 100)).any():
        raise ValueError('pLDDT must be finite and between 0 and 100')
    if not 0 < normalization <= 1:
        raise ValueError('invalid fixed confidence normalization')
    return ((plddt.float()-50)/40).clamp(.05, 1)/normalization
