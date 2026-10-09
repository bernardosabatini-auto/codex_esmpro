"""Joint contextual motif-code flow with isolated-fragment-only inputs."""
import math
import torch
from torch import nn
from torch.nn import functional as F

AMINO_ACIDS = 'ACDEFGHIKLMNPQRSTVWY'


def isolated_features(latent, fragment, sequence, *, length, start):
    """No full-chain array is accepted by this interface."""
    if latent.shape != (20, 8) or fragment.shape != (20, 4, 3):
        raise ValueError('Exactly twenty isolated residues required')
    if len(sequence) != 20 or any(a not in AMINO_ACIDS for a in sequence):
        raise ValueError('Invalid supplied sequence')
    if not 0 <= start <= length-20 or length > 512:
        raise ValueError('Invalid placement')
    if not torch.isfinite(latent).all() or not torch.isfinite(fragment).all():
        raise ValueError('Nonfinite isolated input')
    work = fragment.double()
    origin = work[10, 1]
    x = work[10, 2]-origin
    y = work[10, 0]-origin
    if torch.linalg.vector_norm(x) < 1e-5:
        raise ValueError('Degenerate frame')
    x = F.normalize(x, dim=0)
    y = y-(x*y).sum()*x
    if torch.linalg.vector_norm(y) < 1e-5:
        raise ValueError('Degenerate frame')
    y = F.normalize(y, dim=0)
    frame = torch.stack((x, y, torch.linalg.cross(x, y)), dim=1)
    coordinates = ((work-origin)@frame).reshape(20, 12).float()/10
    index = torch.tensor([AMINO_ACIDS.index(a) for a in sequence], device=latent.device)
    features = torch.cat((latent.float(), F.one_hot(index, 20).float(), coordinates), dim=-1)
    pos = torch.arange(20, device=latent.device, dtype=torch.float32)
    placement = torch.stack((pos/19, (pos+start)/length,
                            torch.full_like(pos, length/512), torch.full_like(pos, start/length)), dim=-1)
    return features, placement


class ContextFlow(nn.Module):
    def __init__(self, width=128, layers=4, heads=4, feedforward=512, dropout=0.):
        super().__init__()
        self.state = nn.Linear(8+4+32, width)
        self.condition = nn.Linear(40, width, bias=False)
        nn.init.zeros_(self.condition.weight)
        self.blocks = nn.ModuleList([
            nn.TransformerEncoderLayer(width, heads, feedforward, dropout,
                                       activation='gelu', batch_first=True, norm_first=True)
            for _ in range(layers)])
        self.norm = nn.LayerNorm(width)
        self.output = nn.Linear(width, 8)
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)
        self.register_buffer('frequencies', torch.exp(torch.linspace(0, math.log(1000), 16)))

    def forward(self, x, time, features, placement):
        angle = time[:, None]*self.frequencies[None]
        temporal = torch.cat((angle.sin(), angle.cos()), dim=-1)
        h = self.state(torch.cat((x, placement, temporal[:, None].expand(-1, 20, -1)), dim=-1))
        h = h+self.condition(features)
        for block in self.blocks:
            h = block(h)
        return self.output(self.norm(h))


@torch.no_grad()
def sample_codes(model, noise, features, placement, *, steps=50):
    x = noise.clone()
    for i in range(steps):
        time = torch.full((len(x),), i/steps, device=x.device, dtype=x.dtype)
        x = x+model(x, time, features, placement)/steps
    if not torch.isfinite(x).all():
        raise ValueError('Nonfinite context samples')
    return x
