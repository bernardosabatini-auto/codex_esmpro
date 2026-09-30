"""Explicit inference precision with restoration of global PyTorch settings."""
from contextlib import contextmanager
import torch

MODES = ('bf16', 'fp16', 'tf32', 'fp32')
HYBRID_MODES = ('fp16_mlp', 'fp16_linear')


class _FP16Module(torch.nn.Module):
    """Lower precision GEMMs, returning to the caller's residual-stream dtype."""
    def __init__(self, inner):
        super().__init__()
        self.inner = inner
        self.train(inner.training)

    def forward(self, x):
        with torch.autocast(x.device.type, dtype=torch.float16):
            result = self.inner(x)
        return result.to(x.dtype)


@contextmanager
def hybrid_modules(model, mode):
    """Temporarily wrap only DiT MLPs and optionally QKV/output projections.

    Attention products, normalization, conditioning, pair track, output head,
    latent integration and decoder remain under the outer FP32 policy. Original
    module identities and state-dict names are restored even after failure.
    """
    if mode not in HYBRID_MODES:
        if mode not in MODES:
            raise ValueError(f'unknown flow precision: {mode}')
        yield
        return
    if model.training:
        raise ValueError('hybrid precision policies are inference-only')
    originals = []
    try:
        for block in model.blocks:
            targets = [(block, 'mlp')]
            if mode == 'fp16_linear':
                targets += [(block.attn, 'qkv'), (block.attn, 'out')]
            for parent, name in targets:
                original = getattr(parent, name)
                if isinstance(original, _FP16Module):
                    raise ValueError('nested hybrid precision contexts are unsupported')
                originals.append((parent, name, original))
                setattr(parent, name, _FP16Module(original))
        yield
    finally:
        for parent, name, original in reversed(originals):
            setattr(parent, name, original)


@contextmanager
def inference_precision(mode):
    if mode not in MODES:
        raise ValueError(f'unknown inference precision: {mode}')
    previous = torch.get_float32_matmul_precision()
    previous_cudnn = torch.backends.cudnn.allow_tf32
    torch.set_float32_matmul_precision('highest' if mode == 'fp32' else 'high')
    torch.backends.cudnn.allow_tf32 = mode != 'fp32'
    try:
        with torch.autocast('cuda', dtype=torch.float16 if mode == 'fp16' else torch.bfloat16,
                            enabled=mode in ('bf16', 'fp16')):
            yield
    finally:
        torch.set_float32_matmul_precision(previous)
        torch.backends.cudnn.allow_tf32 = previous_cudnn
