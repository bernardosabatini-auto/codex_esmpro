"""Decode fixed native latent targets separately from fragment-only generation."""
import torch
from .flow import target_noise


def decode_native_anchors(decoder, latent, *, target_id, seed):
    if latent.ndim!=2 or latent.shape[-1]!=8 or not torch.isfinite(latent).all():
        raise ValueError('Finite native full-structure latent required')
    n=len(latent);z=latent[None].expand(2,-1,-1)
    mask=torch.ones(2,n,dtype=torch.bool,device=z.device)
    noise=torch.cat([target_noise([target_id],[4*n],3,seed=seed,sample_index=k,
                                 stream='decoder:0',device=z.device) for k in range(2)])*decoder.fm.scale_ref
    _,bb=decoder(z,mask,noise=noise,return_backbone=True)
    if bb.shape!=(2,n,4,3) or not torch.isfinite(bb).all():raise ValueError('Invalid native decode')
    return z,bb
