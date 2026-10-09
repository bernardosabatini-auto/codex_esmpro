"""Bind sampled isolated-input codes to the unchanged RePaint scaffold sampler."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha


def identity(path):
    s = Path(path).stat()
    return dict(path=str(Path(path).resolve()),size=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino)


def audit_worker(c):
    payload = {k:v for k,v in c.items() if k!='config_sha256'}
    if hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()!=c['config_sha256']:
        raise ValueError('Changed generation configuration')
    if [identity(r['path']) for r in c['sources']]!=c['file_identity']:
        raise ValueError('Changed CPU-verified source identity')


def audit(c):
    audit_worker(c)
    for source in c['sources']:
        if sha(source['path'])!=source['sha256']:
            raise ValueError('Changed generation source')
    tm=json.loads(Path(c['training_manifest']).read_text());tr=json.loads(Path(c['training_report']).read_text())
    data=json.loads(Path(c['data_manifest']).read_text());om=json.loads(Path(c['oracle_manifest']).read_text())
    if (tm['status']!='complete' or tr['status']!='complete' or not tr['qualified'] or tr['profile_only']
            or tr['manifest_sha256']!=sha(c['training_manifest']) or tm['config']['updates']!=2000
            or tr['data_manifest_sha256']!=sha(c['data_manifest']) or c['spec']!=data['spec']
            or c['selected']!=om['config']['selected'] or c['checkpoint']!=om['config']['checkpoint']
            or c['decoder_checkpoint']!=om['config']['decoder_checkpoint'] or c['fragments']!=om['config']['fragments']
            or c['seed']!=2026100405 or c['allocation_minutes']!=15 or c['work_cap_seconds']!=780):
        raise ValueError('Changed qualified training/sampling lineage')
    evaluation=[r for r in data['records'] if r['split']=='evaluation']
    if len(evaluation)!=32 or {r['id'] for r in evaluation}!={r['id'] for r in c['selected']}:
        raise ValueError('Changed evaluation family panel')
    if c['evaluation_rows']!=evaluation:
        raise ValueError('Changed code-to-protein mapping')
    for arm in data['spec']['arms']:
        x=np.load(c['codes'][arm],allow_pickle=False)
        if sha(c['codes'][arm])!=tr['arms'][arm]['codes_sha256'] or x.shape!=(128,20,8) or not np.isfinite(x).all():
            raise ValueError('Changed learned code samples')
    return data


def main():
    p=argparse.ArgumentParser();p.add_argument('--training',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];run=a.training.resolve()
    tm=json.loads((run/'manifest.json').read_text());dm=Path(tm['config']['data_manifest']);data=json.loads(dm.read_text())
    oracle=root/data['spec']['panel_manifest'];om=json.loads(oracle.read_text());oc=om['config']
    c=dict(spec=data['spec'],selected=oc['selected'],evaluation_rows=[r for r in data['records'] if r['split']=='evaluation'],
           seed=2026100405,allocation_minutes=15,work_cap_seconds=780,sources=[],codes={})
    def bind(key,path):
        path=Path(path).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    for key,path in [('training_manifest',run/'manifest.json'),('training_report',root/'reports'/(run.name+'.json')),
                     ('data_manifest',dm),('oracle_manifest',oracle),('oracle_predictions',oracle.parent/'predictions.h5')]:
        bind(key,path)
    for key in ('checkpoint','decoder_checkpoint','fragments','baseline_manifest','baseline_predictions'):
        bind(key,oc[key])
    for arm in data['spec']['arms']:
        bind(arm+'_codes',run/(arm+'_codes.npy'));c['codes'][arm]=c.pop(arm+'_codes')
    c['file_identity']=[identity(r['path']) for r in c['sources']]
    c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Two arms,256 new outputs,16 historical control samples; one RTX,15min bound')


if __name__=='__main__':main()
