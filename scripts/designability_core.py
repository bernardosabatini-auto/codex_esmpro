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
