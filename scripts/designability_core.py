"""Strict CA-only interchange and complete fixed-budget sequence parsing."""
from pathlib import Path
import numpy as np


def write_ca_pdb(path, ca):
    ca=np.asarray(ca)
    if ca.ndim!=2 or ca.shape[1]!=3 or not np.isfinite(ca).all() or len(ca)>9999:raise ValueError('Invalid CA trace')
    ca=ca-ca.mean(0)
    if np.abs(ca).max()>=999:raise ValueError('PDB coordinate overflow')
    with Path(path).open('w') as f:
        for i,(x,y,z) in enumerate(ca,1):f.write(f'ATOM  {i:5d}  CA  ALA A{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n')
        f.write('TER\nEND\n')


def design_sequences(path, length, count=8):
    records=[];header=None;seq=[]
    for line in Path(path).read_text().splitlines()+['>END']:
        if line.startswith('>'):
            if header and 'sample=' in header:records.append(''.join(seq))
            header=line;seq=[]
        elif line.strip():seq.append(line.strip())
    if len(records)!=count or any(len(s)!=length or set(s)-set('ACDEFGHIKLMNPQRSTVWY') for s in records):raise ValueError('Incomplete or invalid designed sequences')
    return records


def write_backbone_pdb(path, backbone):
    """Export complete supplied backbone atoms without supplying scaffold sequence."""
    bb=np.asarray(backbone)
    if bb.ndim!=3 or bb.shape[1:]!=(4,3) or not len(bb) or len(bb)>9999 or not np.isfinite(bb).all():
        raise ValueError('Invalid complete backbone')
    bb=bb-bb[:,1].mean(0)
    if np.abs(bb).max()>=999:raise ValueError('PDB coordinate overflow')
    with Path(path).open('w') as f:
        for residue,atoms in enumerate(bb,1):
            for offset,(name,xyz) in enumerate(zip(('N','CA','C','O'),atoms)):
                x,y,z=xyz;serial=4*(residue-1)+offset+1
                f.write(f'ATOM  {serial:5d} {name:^4s} ALA A{residue:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           {name[0]}\n')
        f.write('TER\nEND\n')
