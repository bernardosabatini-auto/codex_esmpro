"""Explicit inference precision with restoration of global PyTorch settings."""
from contextlib import contextmanager
import torch

MODES = ('bf16', 'fp16', 'tf32', 'fp32')


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
