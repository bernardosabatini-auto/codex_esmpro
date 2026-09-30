"""Minimal legacy flow architecture. See PROVENANCE.json for copied symbols.

No filesystem changes, environment settings, compilation, or device selection on import.
"""
import math
import torch
from torch import nn
from torch.nn import functional as F

D_LAT, D_ESM = 8, 1280

def timestep_embedding(t, dim, max_period=10000.0):
    half = dim // 2
    freqs = torch.exp(-math.log(max_period) * torch.arange(half, device=t.device) / half)
    args = t[:, None].float() * 1000.0 * freqs[None]
    return torch.cat([torch.cos(args), torch.sin(args)], dim=-1)


class Attention(nn.Module):
    """Multi-head self-attention with a learned relative-position bias and
    key padding, via scaled_dot_product_attention with a float mask."""
    def __init__(self, d, n_heads, rel_pos=32, dropout=0.0):
        super().__init__()
        self.h, self.dh, self.rel = n_heads, d // n_heads, rel_pos
        self.qkv = nn.Linear(d, 3 * d); self.out = nn.Linear(d, d)
        self.bias = nn.Embedding(2 * rel_pos + 1, n_heads)
        nn.init.zeros_(self.bias.weight)
        self.dropout = dropout

    def forward(self, x, mask):
        B, L, D = x.shape
        q, k, v = self.qkv(x).view(B, L, 3, self.h, self.dh).unbind(2)
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))          # (B, H, L, dh)
        pos = torch.arange(L, device=x.device)
        rel = (pos[None, :] - pos[:, None]).clamp(-self.rel, self.rel) + self.rel
        bias = self.bias(rel).permute(2, 0, 1).unsqueeze(0)          # (1, H, L, L)
        pad = torch.zeros(B, 1, 1, L, device=x.device, dtype=bias.dtype)
        pad = pad.masked_fill(~mask[:, None, None, :], float("-inf"))
        o = F.scaled_dot_product_attention(q, k, v, attn_mask=(bias + pad).to(q.dtype),
                                           dropout_p=self.dropout if self.training else 0.0)
        return self.out(o.transpose(1, 2).reshape(B, L, D))


class DiTBlock(nn.Module):
    """Pre-norm transformer block with adaLN-Zero modulation from a global
    conditioning vector (time + pooled sequence condition)."""
    def __init__(self, d, n_heads, rel_pos, dropout):
        super().__init__()
        self.n1 = nn.LayerNorm(d, elementwise_affine=False)
        self.attn = Attention(d, n_heads, rel_pos, dropout)
        self.n2 = nn.LayerNorm(d, elementwise_affine=False)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(approximate="tanh"),
                                 nn.Dropout(dropout), nn.Linear(4 * d, d))
        self.ada = nn.Sequential(nn.SiLU(), nn.Linear(d, 6 * d))
        nn.init.zeros_(self.ada[1].weight); nn.init.zeros_(self.ada[1].bias)

    def forward(self, x, c, mask):
        s1, b1, g1, s2, b2, g2 = self.ada(c).unsqueeze(1).chunk(6, dim=-1)
        x = x + g1 * self.attn(self.n1(x) * (1 + s1) + b1, mask)
        x = x + g2 * self.mlp(self.n2(x) * (1 + s2) + b2)
        return x


class LatentFlowNet(nn.Module):
    def __init__(self, d_model=512, n_layers=12, n_heads=8, dropout=0.0,
                 rel_pos=32, self_cond=True, d_cond=D_ESM, max_len=512):
        super().__init__()
        self.self_cond = self_cond
        self.in_proj = nn.Linear(D_LAT * (2 if self_cond else 1), d_model)
        self.cond_norm = nn.LayerNorm(d_cond)
        self.cond_proj = nn.Linear(d_cond, d_model)
        self.null_cond = nn.Parameter(torch.zeros(1, 1, d_model))   # CFG "no sequence"
        self.pos = nn.Embedding(max_len, d_model)
        self.t_mlp = nn.Sequential(nn.Linear(d_model, d_model), nn.SiLU(), nn.Linear(d_model, d_model))
        self.blocks = nn.ModuleList([DiTBlock(d_model, n_heads, rel_pos, dropout) for _ in range(n_layers)])
        self.out_norm = nn.LayerNorm(d_model, elementwise_affine=False)
        self.out_ada = nn.Sequential(nn.SiLU(), nn.Linear(d_model, 2 * d_model))
        self.out_proj = nn.Linear(d_model, D_LAT)
        nn.init.zeros_(self.out_ada[1].weight); nn.init.zeros_(self.out_ada[1].bias)
        nn.init.zeros_(self.out_proj.weight); nn.init.zeros_(self.out_proj.bias)
        self.d_model = d_model

    def prepare_condition(self, esm, mask, cond_drop=None):
        B, L = mask.shape
        c_tok = self.cond_proj(self.cond_norm(esm.float()))
        if cond_drop is None:
            cond_drop = torch.zeros(B, dtype=torch.bool, device=esm.device)
        c_tok = torch.where(cond_drop[:, None, None], self.null_cond.expand(B, L, -1), c_tok)
        m = mask.unsqueeze(-1).float()
        c_pool = (c_tok * m).sum(1) / m.sum(1).clamp(min=1.0)
        return c_tok, c_pool

    def forward(self, x_t, t, esm, mask, cond_drop=None, x_sc=None, *, prepared=None):
        """x_t: (B,L,8) noisy latent; t: (B,) in [0,1]; esm: (B,L,1280);
        cond_drop: (B,) bool, True = replace the sequence condition with the
        null token; x_sc: (B,L,8) self-conditioning estimate of x1 or None.
        Returns the predicted velocity v = x1 - x0, (B,L,8)."""
        B, L, _ = x_t.shape
        if self.self_cond:
            x_sc = torch.zeros_like(x_t) if x_sc is None else x_sc
            x_in = torch.cat([x_t, x_sc], dim=-1)
        else:
            x_in = x_t
        c_tok, c_pool = self.prepare_condition(esm, mask, cond_drop) if prepared is None else prepared
        h = self.in_proj(x_in) + c_tok + self.pos.weight[:L][None]
        c = self.t_mlp(timestep_embedding(t, self.d_model)) + c_pool
        for blk in self.blocks:
            h = blk(h, c, mask)
        s, b = self.out_ada(c).unsqueeze(1).chunk(2, dim=-1)
        return self.out_proj(self.out_norm(h) * (1 + s) + b)
