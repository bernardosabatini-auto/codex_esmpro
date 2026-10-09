"""Training-only native-code retrieval, with immutable isolated query inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from context_flow_generation import audit_worker,identity
from diagnose_context_retrieval import proper_distances
from prepare_overfit import sha


def random_donors(metadata,query,seed):
    def key(row):
        return hashlib.sha256(f'{seed}:{query["id"]}:donor:{row["family"]}'.encode()).digest(),row['id']
    selected=[];seen=set()
    for r in sorted((r for r in metadata if r['bucket']==query['bucket']),key=key):
        if r['family'] in seen:continue
        seen.add(r['family'])
        value=int.from_bytes(hashlib.sha256(f'{seed}:{query["id"]}:window:{r["id"]}'.encode()).digest()[:8],'little')
        selected.append(dict(r,start=value%(r['length']-19)))
        if len(selected)==4:return selected
    raise ValueError('Insufficient distinct random donor families')


def library_metadata(f,excluded):
    rows=[]
    for ident in sorted(f['train']):
        g=f['train/'+ident];family=str(g.attrs['family'])
        if family in excluded:continue
        n=len(g['reference_z']);rows.append(dict(id=ident,family=family,length=n,bucket=((n+127)//128)*128))
    return rows


def code_block(f,row):
    g=f['train/'+row['id']];st=row['start'];z=g['reference_z'][st:st+20]
    if (str(g.attrs['family'])!=row['family'] or len(g['reference_z'])!=row['length'] or z.shape!=(20,8)
            or not np.isfinite(z).all() or abs(z.mean(-1)).max()>2e-5 or abs(z.std(-1)-1).max()>2e-5):
        raise ValueError('Changed donor or non-native code interface')
    return z


def audit(c):
    audit_worker(c)
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed retrieved-context source')
    spec=json.loads(Path(c['protocol']).read_text());data=json.loads(Path(c['data_manifest']).read_text())
    corpus=json.loads(Path(c['corpus_manifest']).read_text());search=json.loads(Path(c['search_report']).read_text())
    original=json.loads(Path(c['original_generation_manifest']).read_text());parent=original['config']
    excluded={r['family'] for r in data['records'] if r['split']!='train'}
    selected=[next(r for r in parent['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    if (spec!=c['spec'] or c['parent']!=parent or c['selected']!=selected or not c['retrieved_context_profile']
            or c['allocation_minutes']!=10 or c['work_cap_seconds']!=480
            or corpus['status']!='complete' or not corpus['training_gate_passed']
            or search['status']!='complete' or search['fragments_sha256']!=sha(c['library'])
            or search['corpus_manifest_sha256']!=sha(c['corpus_manifest'])
            or search['data_manifest_sha256']!=sha(c['data_manifest'])):
        raise ValueError('Changed retrieval scope or certified data')
    nearest={r['target_id']:r['neighbors'] for r in search['rows']}
    with h5py.File(c['library']) as f,h5py.File(c['inputs']) as inputs,h5py.File(parent['fragments']) as queries:
        metadata=library_metadata(f,excluded)
        if len(metadata)!=7893:raise ValueError('Changed donor exclusions')
        if set(inputs)!={r['id'] for r in selected}:raise ValueError('Changed query panel')
        for q in selected:
            ident=q['id'];wanted=dict(retrieved=nearest[ident],random=random_donors(metadata,q,spec['seed']))
            if wanted!=c['donors'][ident]:raise ValueError('Changed nearest or random selection')
            fragment=queries['train/'+ident+'/conditions/c20_center/fragment'][:]
            for arm,donors in wanted.items():
                if len(donors)!=4 or len({r['family'] for r in donors})!=4 or any(r['family'] in excluded or r['bucket']!=q['bucket'] for r in donors):
                    raise ValueError('Donor leakage or dropped slot')
                expected=np.stack([code_block(f,r) for r in donors])
                if not np.array_equal(inputs[ident+'/'+arm][:],expected):raise ValueError('Changed native code sample')
                if arm=='retrieved':
                    for r in donors:
                        bb=f['train/'+r['id']+'/reference_backbone'][r['start']:r['start']+20,1]
                        rms=float(proper_distances(bb[None],fragment[:,1])[0])
                        dx=np.linalg.norm(bb[:,None]-bb[None,:],axis=-1);dy=np.linalg.norm(fragment[:,None,1]-fragment[None,:,1],axis=-1)
                        drms=float(np.sqrt(np.mean((dx-dy)**2)))
                        if abs(rms-r['ca_rmsd'])>1e-4 or abs(drms-r['drms'])>1e-4:
                            raise ValueError('Nearest-window geometry certificate differs')
    return parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/retrieved_context_profile_protocol.json';spec=json.loads(protocol.read_text())
    original=root/spec['source_generation']/'manifest.json';parent=json.loads(original.read_text())['config']
    dm=root/spec['queries']/'manifest.json';data=json.loads(dm.read_text());cm=root/spec['library']/'manifest.json'
    search=root/spec['search'];nearest={r['target_id']:r['neighbors'] for r in json.loads(search.read_text())['rows']}
    c=dict(retrieved_context_profile=True,parent=parent,spec=spec,selected=[next(r for r in parent['selected'] if r['bucket']==b) for b in (128,256,384,512)],
           allocation_minutes=10,work_cap_seconds=480,sources=[],donors={})
    def bind(key,path):
        path=Path(path).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    for key,path in [('protocol',protocol),('original_generation_manifest',original),('data_manifest',dm),('corpus_manifest',cm),('search_report',search),('library',root/spec['library']/'fragments.h5')]:bind(key,path)
    # Only the frozen generator, numerical-control archive and supplied-query archive are runtime dependencies.
    for key in ('checkpoint','decoder_checkpoint','oracle_predictions','fragments'):
        bind(key,parent[key])
    for key in ('checkpoint','decoder_checkpoint'):
        sidecar=Path(parent[key]+'.meta.json')
        if sidecar.exists():bind(key+'_metadata',sidecar)
    inputs=a.output.with_suffix('.h5').resolve()
    excluded={r['family'] for r in data['records'] if r['split']!='train'}
    with h5py.File(c['library']) as f,h5py.File(inputs,'x') as out:
        metadata=library_metadata(f,excluded)
        for q in c['selected']:
            ident=q['id'];c['donors'][ident]=dict(retrieved=nearest[ident],random=random_donors(metadata,q,spec['seed']))
            for arm,donors in c['donors'][ident].items():out.create_dataset(ident+'/'+arm,data=np.stack([code_block(f,r) for r in donors]))
    bind('inputs',inputs);c['file_identity']=[identity(r['path']) for r in c['sources']]
    c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Four isolated queries; retrieved/random native codes, oracle replay and donor-self controls')


if __name__=='__main__':main()
