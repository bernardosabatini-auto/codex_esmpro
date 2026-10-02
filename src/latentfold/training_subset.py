"""Explicit tail-only adaptation with verifiable frozen parameters."""
import hashlib
import torch


def configure_tail(model, blocks):
    if isinstance(blocks, bool) or not isinstance(blocks, int) or not 0 < blocks < len(model.blocks):
        raise ValueError('tail blocks must be positive and smaller than the network depth')
    prefixes = tuple(f'blocks.{i}.' for i in range(len(model.blocks)-blocks, len(model.blocks))) + ('out_ada.', 'out_proj.', 'out_norm.')
    for name, parameter in model.named_parameters():
        parameter.requires_grad_(name.startswith(prefixes))
    trainable = {name: p.numel() for name, p in model.named_parameters() if p.requires_grad}
    return dict(tail_blocks=blocks, trainable_names=list(trainable), trainable_parameters=sum(trainable.values()),
                total_parameters=sum(p.numel() for p in model.parameters()))


def frozen_digest(model, state=None):
    state = model.state_dict() if state is None else state
    trainable = {name for name, p in model.named_parameters() if p.requires_grad}
    digest = hashlib.sha256()
    for name, value in sorted(state.items()):
        if name in trainable:
            continue
        digest.update(name.encode()+b'\0')
        digest.update(str((value.dtype, tuple(value.shape))).encode()+b'\0')
        digest.update(value.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()
