"""Source verification with explicit rejected rows and no outcome-driven replacement."""
import argparse,hashlib,json,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import h5py
from latentfold.backbone import mapped_backbone
from latentfold.metrics import ca_metrics
from prepare_holdout import AA
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser();p.add_argument('--partition',type=int,choices=range(4),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_broad_source_protocol.json';spec=json.loads(protocol.read_text());candidates=root/'runs'/spec['candidates']/'manifest.json';cm=json.loads(candidates.read_text());pilot=root/'reports'/(spec['pilot']+'.json');pd=json.loads(pilot.read_text());pm=root/'runs'/spec['pilot']/'manifest.json'
    if cm['status']!='complete' or cm['new_proteins']!=7680 or pd['status']!='complete' or not pd['data_gate_passed'] or pd['manifest_sha256']!=sha(pm):raise ValueError('Unqualified broader-data pilot')
    for name,digest in cm['sources'].items():
        if sha(name)!=digest:raise ValueError('Changed sequence-only selection provenance')
    rows=cm['selected'][a.partition::4]
    if len(rows)!=1920:raise ValueError('Changed source partition')
    a.output.mkdir(exist_ok=False);raw=a.output/'source_pdb';raw.mkdir();tick=time.monotonic();m=dict(status='running',partition=a.partition,expected=1920,records=[],rejections=[],sources={str(x):sha(x) for x in (protocol,candidates,pilot,pm,Path(__file__).resolve())},cache=cm['source'],target_ids=[r['id'] for r in rows],scope='Training-only source verification. All frozen candidates accounted for; no geometric training before full data qualification.');atomic_json(a.output/'manifest.json',m)
    existing=[root/'runs/broad_fragment_pilot_sources_20261003/source_pdb',root/'runs/expansion_sources_20261002/source_pdb']
    def fetch(row):
        ident=row['id']
        try:
            if time.monotonic()-tick>3600:raise TimeoutError('Source verification cap')
            if not ident.startswith('AF-') or '/' in ident:raise ValueError('Unsafe source identifier')
            path=next((d/(ident+'.pdb') for d in existing if (d/(ident+'.pdb')).exists()),raw/(ident+'.pdb'))
            if not path.exists():
                for attempt in range(3):
                    try:
                        with urllib.request.urlopen('https://alphafold.ebi.ac.uk/files/'+ident+'.pdb',timeout=45) as response:data=response.read(4*1024**2+1)
                        if len(data)>4*1024**2:raise ValueError('Unexpected source size')
                        path.write_bytes(data);break
                    except Exception:
                        if attempt==2:raise
                        time.sleep(1)
            maps=[];letters=[]
            for line in path.read_text().splitlines():
                if line.startswith('ENDMDL'):break
                if line.startswith('ATOM') and line[12:16].strip()=='CA' and line[16] in (' ','A'):
                    maps.append((line[21],int(line[22:26]),line[26]));letters.append(AA.get(line[17:20].strip(),'X'))
            if ''.join(letters)!=row['sequence'] or len(set(maps))!=len(maps) or any(x[0]!=y[0] or x[1]+1!=y[1] or x[2]!=' ' or y[2]!=' ' for x,y in zip(maps,maps[1:])):raise ValueError('Sequence or contiguous residue mapping mismatch')
            return row,path,maps,mapped_backbone(path,maps),None
        except Exception as error:return row,None,None,None,f'{type(error).__name__}: {error}'
    try:
        with ThreadPoolExecutor(max_workers=2) as pool,h5py.File(cm['source']) as cache,h5py.File(a.output/'backbones.h5','x') as out:
            for row,path,maps,backbone,error in pool.map(fetch,rows):
                if time.monotonic()-tick>3600:raise TimeoutError('Source verification cap')
                ident=row['id']
                if error:m['rejections'].append(dict(id=ident,error=error))
                else:
                    ca=cache['train/'+ident+'/ca_coords'][:]
                    if hashlib.sha256(ca.tobytes()).hexdigest()!=row['array_sha256']['ca_coords']:raise ValueError('Changed cached source CA')
                    rmsd=ca_metrics(backbone[:,1],ca)['ca_rmsd']
                    if rmsd>.02:m['rejections'].append(dict(id=ident,error='Source/cached CA disagreement',ca_rmsd=rmsd))
                    else:
                        g=out.create_group(ident);g.create_dataset('backbone',data=backbone);g.attrs['sequence']=row['sequence'];m['records'].append(dict(id=ident,family=row['family'],length=row['length'],bucket=row['bucket'],sequence_sha256=row['sequence_sha256'],source_pdb=str(path.resolve()),source_sha256=sha(path),residue_map=maps,source_ca_rmsd=rmsd))
                if (len(m['records'])+len(m['rejections']))%32==0:out.flush();atomic_json(a.output/'manifest.json',m)
        if {r['id'] for r in m['records']+m['rejections']}!=set(m['target_ids']) or len(m['records'])+len(m['rejections'])!=1920:raise ValueError('Missing/duplicated source candidate')
        m.update(status='complete',source_gate_passed=len(m['records'])/1920>=.98,backbones_sha256=sha(a.output/'backbones.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)
    print(json.dumps({k:m[k] for k in ('status','partition','source_gate_passed','elapsed_seconds')}))

if __name__=='__main__':main()
