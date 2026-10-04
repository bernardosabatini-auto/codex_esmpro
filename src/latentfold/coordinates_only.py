"""Omit unused post-sampling confidence work on a private inference model."""
from contextlib import contextmanager
import torch


class _NoConfidence(torch.nn.Module):
    def forward(self, **kwargs):
        return {}


@contextmanager
def coordinates_only(model):
    """Caller must seed each fold; confidence outputs are deliberately absent.

    This changes only the post-coordinate confidence call. It is not suitable
    for concurrent calls on the same model or consumers of confidence scores.
    The original module and its weights remain intact and are always restored.
    """
    if model.training or torch.is_grad_enabled():
        raise ValueError('Coordinates-only execution requires eval and no_grad')
    original = model.confidence_head
    if isinstance(original, _NoConfidence):
        raise ValueError('Nested coordinates-only contexts are unsupported')
    try:
        model.confidence_head = _NoConfidence().eval()
        yield
    finally:
        model.confidence_head = original
