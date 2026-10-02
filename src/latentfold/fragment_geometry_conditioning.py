"""Optional direct distance information from supplied fragment atoms only."""
import torch
from torch import nn
from torch.nn import functional as F
from .fragment_conditioning import FragmentAdapter


def fragment_coordinates(fragment, *, length, start):
    if fragment.ndim!=3 or fragment.shape[1:]!=(4,3) or len(fragment)<3 or not torch.isfinite(fragment).all():raise ValueError('Finite supplied fragment backbone required')
    if start<0 or start+len(fragment)>length:raise ValueError('Invalid placement')
    coordinates=fragment.new_zeros(length,3);coordinates[start:start+len(fragment)]=fragment[:,1]
    return coordinates


class FragmentGeometryAdapter(FragmentAdapter):
    """Retain the token adapter; additionally expose known intramotif distances.

    No pair values involving scaffold residues are supplied. Zero initialization
    preserves the original generator, and fragment dropout removes both routes.
    """
    def __init__(self, output_width, *, n_layers, n_heads, hidden=256, pair_hidden=64, distance_precision="fp32", backbone_tokens=False):
        super().__init__(output_width,hidden)
        if distance_precision not in ("fp32","fp64"):raise ValueError("Unsupported distance precision")
        self.distance_precision=distance_precision
        self.n_layers,self.n_heads=n_layers,n_heads
        self.register_buffer('centers',torch.arange(0,32,2,dtype=torch.float32))
        self.pair_hidden=nn.Linear(17,pair_hidden)
        self.pair_output=nn.Linear(pair_hidden,n_layers*n_heads)
        nn.init.zeros_(self.pair_output.weight);nn.init.zeros_(self.pair_output.bias)
        self.backbone_tokens = backbone_tokens
        if backbone_tokens:
            # Preserve all shared initial weights and the caller's random stream.
            with torch.random.fork_rng(devices=[]):
                self.backbone_hidden = nn.Linear(12, hidden)
                self.backbone_output = nn.Linear(hidden, output_width)
                nn.init.zeros_(self.backbone_output.weight)
                nn.init.zeros_(self.backbone_output.bias)

    def forward(self, features, keep, mask, dropped):
        if not self.backbone_tokens:
            return super().forward(features, keep, mask, dropped)
        if features.shape != (*mask.shape, 41) or not torch.isfinite(features).all():
            raise ValueError('Expected latent/sequence plus twelve backbone coordinates')
        if (features[~keep] != 0).any():
            raise ValueError('Scaffold backbone inputs must be absent')
        base = super().forward(features[..., :29], keep, mask, dropped)
        extra = self.backbone_output(F.silu(self.backbone_hidden(features[..., 29:])))
        return base + extra * (keep & ~dropped[:, None])[..., None]

    def pair_biases(self,coordinates,keep,mask,dropped):
        if coordinates.shape!=(*mask.shape,3) or keep.shape!=mask.shape or dropped.shape!=mask.shape[:1]:raise ValueError('Invalid pair conditioning shapes')
        if mask.dtype!=torch.bool or keep.dtype!=torch.bool or dropped.dtype!=torch.bool or (keep&~mask).any() or not keep.any(1).all():raise ValueError('Invalid conditioning masks')
        if not torch.isfinite(coordinates).all() or (coordinates[~keep]!=0).any():raise ValueError('Scaffold coordinates must be absent')
        work=coordinates.double() if self.distance_precision=='fp64' else coordinates.float()
        distance=torch.cdist(work,work,compute_mode='donot_use_mm_for_euclid_dist').float()
        rbf=torch.exp(-.5*((distance[...,None]-self.centers)/2).square());features=torch.cat((rbf,(distance/(distance+10))[...,None]),-1)
        delta=self.pair_output(F.silu(self.pair_hidden(features)))
        known=keep[:,:,None]&keep[:,None,:]&~dropped[:,None,None]
        delta=(delta*known[...,None]).permute(0,3,1,2).contiguous()
        return delta.split(self.n_heads,dim=1)
