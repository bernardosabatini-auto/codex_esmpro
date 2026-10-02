"""Verify AFDB full backbones for a frozen training or tuning split."""
import argparse,hashlib,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request
import h5py,numpy as np
from latentfold.backbone import mapped_backbone
from latentfold.metrics import ca_metrics
from prepare_holdout import AA
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for name in ('selection','existing','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--split',choices=('train','tuning'),default='train')
    p.add_argument('--expected-count',type=int)
    a=p.parse_args();selection=json.loads(a.selection.read_text());rows=selection[a.split];expected=a.expected_count if a.expected_count is not None else (512 if a.split=='train' else 64)
    if selection.get('status')=='candidate_inventory':
        audit=json.loads(Path(selection['source_audit']).read_text())
        if a.split!='train' or audit['status']!='complete' or audit['candidate_manifest_sha256']!=hashlib.sha256(a.selection.read_bytes()).hexdigest() or expected!=audit['candidates']:raise ValueError('expansion audit changed or incomplete')
    if not 1<=expected<=4096:raise ValueError('invalid expected count')
    if len(rows)!=expected:raise ValueError('wrong number of frozen families')
    a.output.mkdir(parents=True,exist_ok=False);raw=a.output/'source_pdb';raw.mkdir();m=dict(status='running',split=a.split,expected=expected,records=[],selection_sha256=hashlib.sha256(a.selection.read_bytes()).hexdigest(),scope='AFDB predicted source structures, not experimental native conformations');atomic_json(a.output/'manifest.json',m)
    def fetch(row):
        ident=row['id']
        if not ident.startswith('AF-') or '/' in ident:raise ValueError('expected safe AFDB identifier')
        existing=a.existing/(ident+'.pdb');path=existing if existing.exists() else raw/(ident+'.pdb')
        if not path.exists():
            with urllib.request.urlopen('https://alphafold.ebi.ac.uk/files/'+ident+'.pdb',timeout=45) as response:data=response.read(4*1024**2)
            path.write_bytes(data)
        maps=[];letters=[]
        for line in path.read_text().splitlines():
            if line.startswith('ENDMDL'):break
            if line.startswith('ATOM') and line[12:16].strip()=='CA' and line[16] in (' ','A'):
                maps.append((line[21],int(line[22:26]),line[26]));letters.append(AA.get(line[17:20].strip(),'X'))
        if ''.join(letters)!=row['sequence'] or len(set(maps))!=len(maps):raise ValueError('source sequence/residue mapping mismatch: '+ident)
        backbone=mapped_backbone(path,maps)
        return row,path,maps,backbone
    try:
        with ThreadPoolExecutor(max_workers=4) as pool,h5py.File(selection['dataset']) as source,h5py.File(a.output/'backbones.h5','x') as target:
            for row,path,maps,backbone in pool.map(fetch,rows):
                cached=source['train'][row['id']]['ca_coords'][:];rmsd=ca_metrics(backbone[:,1],cached)['ca_rmsd']
                if rmsd>.02:raise ValueError('AFDB source differs from inherited coordinates: '+row['id'])
                g=target.create_group(row['id']);g.create_dataset('backbone',data=backbone);g.attrs['sequence']=row['sequence']
                m['records'].append(dict(id=row['id'],family=row['family'],length=row['length'],sequence_sha256=row['sequence_sha256'],source_pdb=str(path.resolve()),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),residue_map=maps,source_ca_rmsd=rmsd))
                if len(m['records'])%16==0:target.flush();atomic_json(a.output/'manifest.json',m);print('verified teacher source',len(m['records']),flush=True)
        m.update(status='complete',dataset=str((a.output/'backbones.h5').resolve()))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
