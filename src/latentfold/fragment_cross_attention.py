"""Dynamic access to supplied fragment tokens, with no scaffold input features."""
import torch
from torch import nn
from torch.nn import functional as F

from .fragment_geometry_conditioning import FragmentGeometryAdapter


class FragmentCrossAttentionAdapter(FragmentGeometryAdapter):
    """Add a zero-initialized residual after each frozen generator block.

    Both routing arms perform identical attention operations. Only the output
    gate differs: all valid residues versus supplied motif residues. Memory is
    packed once per conditioning call and reused throughout the flow trajectory.
    Existing fragment tokens already contain isolated ProteinAE codes and the
    supplied sequence. No scaffold coordinates, codes or sequence enter memory.
    """
    def __init__(self, output_width, *, cross_width=128, cross_heads=4,
                 cross_route='all', **kwargs):
        super().__init__(output_width, **kwargs)
        if cross_route not in ('all', 'motif'):
            raise ValueError('Unknown fragment cross-attention route')
        if cross_width < 1 or cross_heads < 1 or cross_width % cross_heads:
            raise ValueError('Invalid cross-attention dimensions')
        if self.backbone_tokens:
            raise ValueError('Cross attention consumes isolated latent/sequence tokens only')
        self.cross_width, self.cross_heads = cross_width, cross_heads
        self.cross_route = cross_route
        self.cross_memory = nn.Sequential(nn.Linear(29, cross_width), nn.SiLU(),
                                          nn.Linear(cross_width, 2 * cross_width))
        self.cross_queries = nn.ModuleList(nn.Linear(output_width, cross_width)
                                           for _ in range(self.n_layers))
        self.cross_outputs = nn.ModuleList(nn.Linear(cross_width, output_width)
                                           for _ in range(self.n_layers))
        self.cross_relative = nn.Embedding(65, cross_heads)
        nn.init.zeros_(self.cross_relative.weight)
        for output in self.cross_outputs:
            nn.init.zeros_(output.weight)
            nn.init.zeros_(output.bias)

    def load_parent(self, state):
        """Only new cross-attention keys may be absent from the parent."""
        missing, unexpected = self.load_state_dict(state, strict=False)
        expected = {k for k in self.state_dict() if k.startswith('cross_')}
        if unexpected or set(missing) != expected:
            raise ValueError('Incompatible parent fragment adapter')

    def freeze_parent(self):
        for name, parameter in self.named_parameters():
            parameter.requires_grad_(name.startswith('cross_'))

    def cross_condition(self, features, keep, mask, dropped):
        # Reuse the parent's strict validation before packing any data.
        super().forward(features, keep, mask, dropped)
        batch, length = mask.shape
        counts = keep.sum(1)
        width = int(counts.max())
        positions = torch.arange(length, device=keep.device).expand(batch, -1)
        indices = positions.masked_fill(~keep, length).sort(1).values[:, :width]
        valid = indices < length
        indices = indices.clamp_max(length - 1)
        packed = features.gather(1, indices[..., None].expand(-1, -1, 29))
        packed = packed * valid[..., None]
        keys, values = self.cross_memory(packed).chunk(2, -1)
        shape = (batch, width, self.cross_heads, self.cross_width // self.cross_heads)
        keys, values = (v.reshape(shape).transpose(1, 2) for v in (keys, values))
        relative = (indices[:, None, :] - positions[:, :, None]).clamp(-32, 32) + 32
        bias = self.cross_relative(relative).permute(0, 3, 1, 2)
        bias = bias.masked_fill(~valid[:, None, None, :], float('-inf'))
        gate = (mask if self.cross_route == 'all' else keep) & ~dropped[:, None]
        return keys, values, bias, gate[..., None]

    def cross_update(self, hidden, layer, memory):
        keys, values, bias, gate = memory
        batch, length, _ = hidden.shape
        query = self.cross_queries[layer](F.layer_norm(hidden, (hidden.shape[-1],)))
        query = query.reshape(batch, length, self.cross_heads, -1).transpose(1, 2)
        attended = F.scaled_dot_product_attention(query, keys, values,
                                                  attn_mask=bias, dropout_p=0.)
        attended = attended.transpose(1, 2).reshape(batch, length, self.cross_width)
        return hidden + self.cross_outputs[layer](attended) * gate
