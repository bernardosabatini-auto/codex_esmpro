"""Optional legacy pair track, with explicit configuration and no monkey patching."""
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
from .model import D_LAT, D_ESM, DiTBlock, timestep_embedding

class PairAttention(nn.Module):
    """Self-attention with a learned relative-position bias PLUS an external
    per-head pair bias (B, H, L, L) from the pair track."""
    def __init__(self, d, n_heads, d_pair, rel_pos=32, dropout=0.0):
        super().__init__()
        self.h, self.dh, self.rel = n_heads, d // n_heads, rel_pos
        self.qkv = nn.Linear(d, 3 * d); self.out = nn.Linear(d, d)
        self.bias = nn.Embedding(2 * rel_pos + 1, n_heads); nn.init.zeros_(self.bias.weight)
        self.dropout = dropout

    def forward(self, x, mask, pb):
        """pb: (B,H,L,L) pair bias for this layer (precomputed once for all layers)."""
        B, L, D = x.shape
        q, k, v = self.qkv(x).view(B, L, 3, self.h, self.dh).unbind(2)
        q, k, v = (t.transpose(1, 2) for t in (q, k, v))
        pos = torch.arange(L, device=x.device)
        rel = (pos[None, :] - pos[:, None]).clamp(-self.rel, self.rel) + self.rel
        bias = self.bias(rel).permute(2, 0, 1).unsqueeze(0)                       # (1,H,L,L)
        pad = torch.zeros(B, 1, 1, L, device=x.device, dtype=bias.dtype).masked_fill(~mask[:, None, None, :], float("-inf"))
        o = F.scaled_dot_product_attention(q, k, v, attn_mask=(bias.to(q.dtype) + pb.to(q.dtype) + pad.to(q.dtype)),
                                           dropout_p=self.dropout if self.training else 0.0)
        return self.out(o.transpose(1, 2).reshape(B, L, D))


class PairDiTBlock(DiTBlock):
    def __init__(self, d, n_heads, rel_pos, dropout, d_pair):
        super().__init__(d, n_heads, rel_pos, dropout)
        self.attn = PairAttention(d, n_heads, d_pair, rel_pos, dropout)

    def forward(self, x, c, mask, pb):
        s1, b1, g1, s2, b2, g2 = self.ada(c).unsqueeze(1).chunk(6, dim=-1)
        x = x + g1 * self.attn(self.n1(x) * (1 + s1) + b1, mask, pb)
        x = x + g2 * self.mlp(self.n2(x) * (1 + s2) + b2)
        return x


class TriangleMultiply(nn.Module):
    """AlphaFold2 triangular multiplicative update, outgoing (mode 'out') or
    incoming ('in'), gated. p: (B,L,L,d). O(L^3 d)."""
    def __init__(self, d, mode):
        super().__init__()
        self.mode = mode
        self.norm_in = nn.LayerNorm(d)
        self.a = nn.Linear(d, d); self.b = nn.Linear(d, d)
        self.ga = nn.Linear(d, d); self.gb = nn.Linear(d, d)
        self.norm_out = nn.LayerNorm(d)
        self.out = nn.Linear(d, d); self.gate = nn.Linear(d, d)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)   # residual starts at identity

    def forward(self, p, pmask):
        z = self.norm_in(p)
        a = torch.sigmoid(self.ga(z)) * self.a(z) * pmask
        b = torch.sigmoid(self.gb(z)) * self.b(z) * pmask
        if self.mode == "out":   # sum_k a_ik b_jk
            x = torch.einsum("bikd,bjkd->bijd", a, b)
        else:                    # sum_k a_ki b_kj
            x = torch.einsum("bkid,bkjd->bijd", a, b)
        return torch.sigmoid(self.gate(z)) * self.out(self.norm_out(x))


class TriangleMultiplyFused(TriangleMultiply):
    """Same computation as TriangleMultiply with the five per-pair projections (a, b, their
    gates, the output gate) fused into one GEMM on the (B*L*L, d) pair matrix: 5 launches ->
    1, better tensor-core utilisation, same parameter count."""
    def __init__(self, d, mode):
        nn.Module.__init__(self)
        self.mode = mode
        self.norm_in = nn.LayerNorm(d)
        self.proj = nn.Linear(d, 5 * d)
        self.norm_out = nn.LayerNorm(d)
        self.out = nn.Linear(d, d)
        nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)

    def forward(self, p, pmask):
        z = self.norm_in(p)
        a_, b_, ga, gb, g = self.proj(z).chunk(5, dim=-1)
        a = torch.sigmoid(ga) * a_ * pmask
        b = torch.sigmoid(gb) * b_ * pmask
        if self.mode == "out":
            x = torch.einsum("bikd,bjkd->bijd", a, b)
        else:
            x = torch.einsum("bkid,bkjd->bijd", a, b)
        return torch.sigmoid(g) * self.out(self.norm_out(x))


class PairBlock(nn.Module):
    def __init__(self, d, dropout=0.0, fused=False):
        super().__init__()
        TM = TriangleMultiplyFused if fused else TriangleMultiply
        self.tri_out = TM(d, "out"); self.tri_in = TM(d, "in")
        self.norm = nn.LayerNorm(d)
        self.trans = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(approximate="tanh"), nn.Dropout(dropout), nn.Linear(4 * d, d))
        nn.init.zeros_(self.trans[-1].weight); nn.init.zeros_(self.trans[-1].bias)

    def forward(self, p, pmask):
        p = p + self.tri_out(p, pmask)
        p = p + self.tri_in(p, pmask)
        p = p + self.trans(self.norm(p)) * pmask
        return p


class PairTrack(nn.Module):
    """Build and refine the pair representation from the conditioning."""
    def __init__(self, d_in, d_pair=64, n_blocks=6, rel_pos=32, use_contact=False, n_dist_bins=0, dropout=0.0, fused=False, checkpoint_blocks=False):
        super().__init__()
        self.checkpoint_blocks = checkpoint_blocks
        self.rel = rel_pos
        self.norm_s = nn.LayerNorm(d_in)
        self.left = nn.Linear(d_in, d_pair); self.right = nn.Linear(d_in, d_pair)
        self.relpos = nn.Embedding(2 * rel_pos + 1, d_pair)
        self.use_contact = use_contact
        self.contact = nn.Linear(1, d_pair) if use_contact else None
        self.n_dist_bins = n_dist_bins
        self.dist = nn.Linear(n_dist_bins, d_pair) if n_dist_bins else None   # recycling hook
        self.blocks = nn.ModuleList([PairBlock(d_pair, dropout, fused) for _ in range(n_blocks)])
        self.norm_out = nn.LayerNorm(d_pair)

    def forward(self, s, mask, contact=None, dist_feats=None):
        B, L, _ = s.shape
        z = self.norm_s(s.float())
        p = self.left(z).unsqueeze(2) + self.right(z).unsqueeze(1)               # (B,L,L,d)
        pos = torch.arange(L, device=s.device)
        rel = (pos[None, :] - pos[:, None]).clamp(-self.rel, self.rel) + self.rel
        p = p + self.relpos(rel).unsqueeze(0)
        if self.use_contact and contact is not None:
            p = p + self.contact(contact.float().unsqueeze(-1))
        if self.dist is not None:
            if dist_feats is not None:
                p = p + self.dist(dist_feats.float())
            else:   # no geometry this step: still touch the parameters so DDP sees them every iteration
                p = p + self.dist.bias + 0.0 * self.dist.weight.sum()
        # Honor the caller's precision policy, including a true FP32 reference.
        if p.is_cuda and torch.is_autocast_enabled('cuda'):
            p = p.to(torch.get_autocast_dtype('cuda'))
        pmask = (mask[:, :, None] & mask[:, None, :]).unsqueeze(-1).to(p.dtype)
        p = p * pmask
        for blk in self.blocks:
            # activation checkpointing: keep only the block input, recompute the
            # ~10 L x L x d intermediates in backward (memory 10x smaller)
            if torch.is_grad_enabled() and self.checkpoint_blocks:
                p = checkpoint(blk, p, pmask, use_reentrant=False)
            else:
                p = blk(p, pmask)
        return self.norm_out(p.float())


class PairFlowNet(nn.Module):
    """Gate 7 LatentFlowNet + PairTrack; same forward signature plus optional
    `contact` and `dist_feats`, and a `pair` kwarg to reuse a precomputed pair
    tensor (self-conditioning pass, sampling steps)."""
    def __init__(self, d_model=768, n_layers=16, n_heads=12, dropout=0.0, rel_pos=32, self_cond=True,
                 d_cond=D_ESM, d_pair=64, n_pair_blocks=6, pair_contact=False, pair_dist_bins=0, pair_fused=False, max_len=512, checkpoint_blocks=False):
        super().__init__()
        self.self_cond = self_cond
        self.checkpoint_blocks = checkpoint_blocks
        self.in_proj = nn.Linear(D_LAT * (2 if self_cond else 1), d_model)
        self.cond_norm = nn.LayerNorm(d_cond); self.cond_proj = nn.Linear(d_cond, d_model)
        self.null_cond = nn.Parameter(torch.zeros(1, 1, d_model))
        self.pos = nn.Embedding(max_len, d_model)
        self.t_mlp = nn.Sequential(nn.Linear(d_model, d_model), nn.SiLU(), nn.Linear(d_model, d_model))
        self.pair = PairTrack(d_cond, d_pair, n_pair_blocks, rel_pos, pair_contact, pair_dist_bins, dropout, fused=pair_fused, checkpoint_blocks=checkpoint_blocks)
        self.null_pair = nn.Parameter(torch.zeros(1, 1, 1, d_pair))
        self.pair_bias_norm = nn.LayerNorm(d_pair)
        self.pair_bias = nn.Linear(d_pair, n_layers * n_heads, bias=False); nn.init.zeros_(self.pair_bias.weight)
        self.n_heads = n_heads
        self.blocks = nn.ModuleList([PairDiTBlock(d_model, n_heads, rel_pos, dropout, d_pair) for _ in range(n_layers)])
        self.out_norm = nn.LayerNorm(d_model, elementwise_affine=False)
        self.out_ada = nn.Sequential(nn.SiLU(), nn.Linear(d_model, 2 * d_model))
        self.out_proj = nn.Linear(d_model, D_LAT)
        nn.init.zeros_(self.out_ada[1].weight); nn.init.zeros_(self.out_ada[1].bias)
        nn.init.zeros_(self.out_proj.weight); nn.init.zeros_(self.out_proj.bias)
        self.d_model = d_model

    def compute_pair(self, esm, mask, contact=None, dist_feats=None):
        return self.pair(esm, mask, contact, dist_feats)

    def prepare_condition(self, esm, mask, cond_drop=None, *, pair=None, contact=None, dist_feats=None):
        B, L = mask.shape
        if cond_drop is None:
            cond_drop = torch.zeros(B, dtype=torch.bool, device=esm.device)
        c_tok = self.cond_proj(self.cond_norm(esm.float()))
        c_tok = torch.where(cond_drop[:, None, None], self.null_cond.expand(B, L, -1), c_tok)
        if pair is None:
            pair = self.compute_pair(esm, mask, contact, dist_feats)
        pair = torch.where(cond_drop[:, None, None, None], self.null_pair.expand(B, L, L, -1), pair)
        m = mask.unsqueeze(-1).float()
        c_pool = (c_tok * m).sum(1) / m.sum(1).clamp(min=1.0)
        pb_all = self.pair_bias(self.pair_bias_norm(pair)).permute(0, 3, 1, 2)
        if pb_all.is_cuda and torch.is_autocast_enabled('cuda'):
            pb_all = pb_all.to(torch.get_autocast_dtype('cuda'))
        pbs = pb_all.contiguous().split(self.n_heads, dim=1)
        return c_tok, c_pool, pbs

    def forward(self, x_t, t, esm, mask, cond_drop=None, x_sc=None, pair=None, contact=None, dist_feats=None, *, prepared=None):
        B, L, _ = x_t.shape
        if self.self_cond:
            x_sc = torch.zeros_like(x_t) if x_sc is None else x_sc
            x_in = torch.cat([x_t, x_sc], dim=-1)
        else:
            x_in = x_t
        c_tok, c_pool, pbs = self.prepare_condition(esm, mask, cond_drop, pair=pair, contact=contact, dist_feats=dist_feats) if prepared is None else prepared
        h = self.in_proj(x_in) + c_tok + self.pos.weight[:L][None]
        c = self.t_mlp(timestep_embedding(t, self.d_model)) + c_pool
        for blk, pb in zip(self.blocks, pbs):
            if self.checkpoint_blocks and torch.is_grad_enabled():
                h = checkpoint(blk, h, c, mask, pb, use_reentrant=False)
            else:
                h = blk(h, c, mask, pb)
        s, b = self.out_ada(c).unsqueeze(1).chunk(2, dim=-1)
        return self.out_proj(self.out_norm(h) * (1 + s) + b)
