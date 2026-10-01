"""Explicit complete-backbone inputs for ProteinAE reconstruction diagnostics."""
from pathlib import Path
import numpy as np
import torch


def align_backbone_to_reference(backbone, reference, alignment_mask):
    """Fit a proper CA rotation on a shared core and transform every atom.

    Backbone is [B,L,4,3], reference is [L,4,3], mask is boolean [L].
    The caller must define core eligibility before examining model outcomes.
    This helper neither filters samples nor supplies references at inference.
    """
    if (backbone.ndim != 4 or backbone.shape[2:] != (4, 3) or
            reference.shape != backbone.shape[1:] or
            alignment_mask.shape != backbone.shape[1:2] or alignment_mask.dtype != torch.bool or
            not backbone.is_floating_point() or not reference.is_floating_point()):
        raise ValueError('expected complete backbone batch, matching reference and shared boolean core')
    if (backbone.device != reference.device or backbone.device != alignment_mask.device or
            not torch.isfinite(backbone).all() or not torch.isfinite(reference).all() or
            alignment_mask.sum() < 3):
        raise ValueError('invalid alignment coordinates, devices or core')
    source = backbone[:, alignment_mask, 1].double()
    target = reference[alignment_mask, 1].double()
    origin = source.mean(1, keepdim=True)
    destination = target.mean(0, keepdim=True)
    source = source - origin
    target = target - destination
    u, singular, vh = torch.linalg.svd(source.transpose(1, 2) @ target)
    if (singular[:, 1] < 1e-8).any():
        raise ValueError('collinear or degenerate alignment core')
    correction = torch.ones(len(backbone), 3, device=backbone.device, dtype=torch.float64)
    correction[:, -1] = torch.where(torch.linalg.det(u @ vh) < 0, -1., 1.)
    rotation = (u * correction[:, None, :]) @ vh
    aligned = torch.einsum('bnai,bij->bnaj', backbone.double() - origin[:, :, None], rotation)
    return (aligned + destination[None, :, None]).to(backbone.dtype)


def canonical_backbone_frame(backbone):
    """Fix rigid pose using the first residue's complete N/CA/C frame.

    This preserves internal geometry and chirality. It is intended for complete
    sequence backbones; it does not choose an anchor across missing residues.
    """
    if backbone.ndim!=4 or backbone.shape[2:]!=(4,3) or backbone.shape[1]<1 or not torch.isfinite(backbone).all():raise ValueError('expected finite complete backbone batch')
    origin=backbone[:,0,1];axis=backbone[:,0,2]-origin;length=axis.norm(dim=-1,keepdim=True)
    if (length<1e-5).any():raise ValueError('degenerate CA-C axis')
    x=axis/length;offset=backbone[:,0,0]-origin;y=offset-(offset*x).sum(-1,keepdim=True)*x;length=y.norm(dim=-1,keepdim=True)
    if (length<1e-5).any():raise ValueError('collinear first-residue frame')
    y=y/length;z=torch.linalg.cross(x,y,dim=-1);basis=torch.stack((x,y,z),dim=-1)
    return torch.einsum('bnai,bij->bnaj',backbone-origin[:,None,None,:],basis)


def mapped_backbone(pdb_path, residue_map):
    atoms={}
    for line in Path(pdb_path).read_text().splitlines():
        if line.startswith('ENDMDL'):
            break
        if not line.startswith('ATOM') or line[16] not in (' ', 'A'):
            continue
        name=line[12:16].strip()
        if name not in ('N','CA','C','O'):
            continue
        key=(line[21],int(line[22:26]),line[26],name)
        if key in atoms:
            raise ValueError('ambiguous alternate backbone atom')
        atoms[key]=[float(line[30:38]),float(line[38:46]),float(line[46:54])]
    result=np.asarray([[atoms[(*residue,name)] for name in ('N','CA','C','O')] for residue in residue_map],dtype=np.float32)
    if result.shape!=(len(residue_map),4,3) or not np.isfinite(result).all():
        raise ValueError('invalid complete backbone')
    return result


@torch.no_grad()
def encode_backbone(decoder, backbone_angstrom, mask):
    if backbone_angstrom.shape!=(*mask.shape,4,3) or mask.dtype!=torch.bool:
        raise ValueError('expected backbone [B,L,4,3] and boolean mask [B,L]')
    if not torch.isfinite(backbone_angstrom).all() or not mask.any(dim=1).all():
        raise ValueError('invalid encoder coordinates or empty protein')
    atom_mask=mask.repeat_interleave(4,dim=1)
    coords=backbone_angstrom.reshape(mask.shape[0],4*mask.shape[1],3)/10
    coords=decoder.fm._mask_and_zero_com(coords,atom_mask)
    z=decoder.ae_model.encoder(dict(x_1=coords,mask=mask,coords_mask=atom_mask))['single_repr']
    if z.shape!=(*mask.shape,8) or not torch.isfinite(z).all():
        raise ValueError('unexpected encoded latent')
    return z
