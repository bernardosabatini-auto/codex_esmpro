"""Explicit complete-backbone inputs for ProteinAE reconstruction diagnostics."""
from pathlib import Path
import numpy as np
import torch


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
