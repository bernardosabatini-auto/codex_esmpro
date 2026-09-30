"""Select fixed training records and verify local maps against source PDBs."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
import h5py
import numpy as np
from latentfold.metrics import ca_metrics


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); data=a.source/'data/phase1_dataset'
    buckets={128:[],256:[],384:[],512:[]}
    for filename in ('dataset_100k_esmc.h5','dataset_afdb_long_0_esmc.h5'):
        with h5py.File(data/filename,'r') as f:
            for name in f['train']:
                g=f['train'][name]; n=g['z'].shape[0]
                if not 32 <= n <= 512: continue
                bucket=next(k for k in buckets if n<=k)
                if len(buckets[bucket])>=4: continue
                seq=str(g.attrs['sequence']); ca=g['ca_coords'][:]
                adj=[False]*(n-1); residue_map=None
                pdb=a.output.parent/'source_pdb'/f'{name}.pdb'
                if not pdb.exists():
                    pdb.parent.mkdir(parents=True,exist_ok=True)
                    with urllib.request.urlopen(f'https://alphafold.ebi.ac.uk/files/{name}.pdb',timeout=30) as response:
                        pdb.write_bytes(response.read())
                if pdb.exists():
                    rows=[]; seen=set()
                    for line in pdb.read_text().splitlines():
                        if line.startswith('ENDMDL'): break
                        if line.startswith('ATOM') and line[12:16].strip()=='CA':
                            key=(line[21],int(line[22:26]),line[26])
                            if key in seen: continue
                            seen.add(key); rows.append((key,[float(line[30:38]),float(line[38:46]),float(line[46:54])]))
                    if len(rows)!=n or ca_metrics(np.array([r[1] for r in rows]),ca)['ca_rmsd']>.02:
                        raise ValueError(f'{name}: source PDB and cached coordinates differ')
                    residue_map=[list(r[0]) for r in rows]
                    adj=[x[0]==y[0] and x[1]+1==y[1] and x[2]==y[2]==' ' for x,y in zip(residue_map,residue_map[1:])]
                buckets[bucket].append(dict(id=name,file=str(data/filename),split='train',length=n,
                    sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),adjacent=adj,
                    residue_map=residue_map,source_pdb=str(pdb) if pdb.exists() else None))
                required=(128,256) if filename=='dataset_100k_esmc.h5' else (384,512)
                if all(len(buckets[k])==4 for k in required): break
    if any(len(v)!=4 for v in buckets.values()): raise ValueError('incomplete target selection')
    result=dict(purpose='training-only gradient diagnostic; no checkpoint optimization',
                selection='first four IDs per length bucket, fixed before GPU results',
                targets=[r for v in buckets.values() for r in v],buckets={k:[r['id'] for r in v] for k,v in buckets.items()})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(count=len(result['targets']),lengths=[r['length'] for r in result['targets']],
        mapped=sum(r['residue_map'] is not None for r in result['targets']))))

if __name__=='__main__': main()
