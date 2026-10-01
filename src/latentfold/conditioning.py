"""Bounded residual conditioning for a matched early-layer adaptation screen."""
import torch
from torch import nn
from torch.nn import functional as F


class ResidualConditioner(nn.Module):
    """Start exactly at the inherited final-layer conditioner.

    The flow head stays fixed. Arms differ only in features feeding an equally
    sized bottleneck: final layer, layer 60, or a learned four-layer scalar mix.
    The mixture adds four scalar parameters; all share the same residual bound.
    """
    def __init__(self, arm, *, width=128, bound=.1):
        super().__init__()
        if arm not in ('final','layer60','mixture') or width<1 or not 0<bound<=1:raise ValueError('invalid conditioner')
        self.arm=arm;self.bound=bound;self.down=nn.Linear(2560,width,bias=False);self.up=nn.Linear(width,2560,bias=False)
        nn.init.zeros_(self.up.weight)
        self.logits=nn.Parameter(torch.zeros(4)) if arm=='mixture' else None
    def forward(self,layers,mask,*,return_residual=False):
        if set(layers)!={20,40,60,80} or mask.dtype!=torch.bool:raise ValueError('need four selected layers and boolean mask')
        if any(x.shape!=(*mask.shape,2560) for x in layers.values()):raise ValueError('layer dimensions differ')
        if self.arm=='mixture':
            weights=self.logits.softmax(0);value=sum(w*F.layer_norm(layers[k],(2560,)) for w,k in zip(weights,(20,40,60,80)))
        else:value=F.layer_norm(layers[80 if self.arm=='final' else 60],(2560,))
        residual=self.bound*torch.tanh(self.up(F.silu(self.down(value))))*mask[...,None]
        value=(layers[80]+residual)*mask[...,None]
        return (value,residual) if return_residual else value
