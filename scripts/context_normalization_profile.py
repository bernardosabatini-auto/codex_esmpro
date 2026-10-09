"""Audit a missing latent-interface projection without rewriting the failed assay."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from torch.nn import functional as F
from context_flow_generation import audit as audit_source, audit_worker, identity
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from prepare_overfit import sha


def project(codes):
    if codes.shape[-2:]!=(20,8) or not torch.isfinite(codes).all():
        raise ValueError('Finite20x8codes required')
    if (codes.var(-1,unbiased=False)<1e-8).any():
        raise ValueError('Degenerate context code')
    return F.layer_norm(codes,(8,))


def audit(c):
    audit_worker(c)
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed normalization-profile source')
    gm=json.loads(Path(c['source_manifest']).read_text());gd=json.loads(Path(c['source_report']).read_text())
    parent=gm['config'];audit_source(parent)
    spec=json.loads(Path(c['protocol']).read_text())
    selected=[next(r for r in parent['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    if (gm['status']!='complete' or gd['status']!='complete' or gd['manifest_sha256']!=sha(c['source_manifest'])
            or gd['predictions_sha256']!=sha(c['source_predictions']) or spec!=c['spec']
            or c['parent']!=parent or c['selected']!=selected or not c['context_normalization_profile']
            or Path(c['source_manifest']).parent.name!=Path(spec['source_generation']).name):
        raise ValueError('Changed fixed profile lineage')
    return parent


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text())
    if m['status']!='complete':return dict(status='failed',qualified=False,error=m.get('error'))
    c=m['config'];parent=audit(c);path=run/'predictions.h5'
    if sha(path)!=m['predictions_sha256']:raise ValueError('Changed profile outputs')
    lookup={r['id']:r for r in parent['evaluation_rows']}
    codes={arm:np.load(p,allow_pickle=False).reshape(32,4,20,8) for arm,p in parent['codes'].items()}
    records=[];controls=[]
    with h5py.File(path) as f,h5py.File(parent['fragments']) as fr,h5py.File(parent['oracle_predictions']) as oracle,h5py.File(c['source_predictions']) as original:
        if set(f)!={'oracle_original',*c['spec']['arms']}:raise ValueError('Wrong profile arms')
        for arm in f:
            if set(f[arm])!={r['id'] for r in c['selected']}:raise ValueError('Dropped profile targets')
        for row in c['selected']:
            ident=row['id'];n=row['length'];q=fr['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
            native=oracle['new/'+ident+'/target'][:,st:st+20]
            for arm in ('oracle_original',*c['spec']['arms']):
                original_codes=native if arm.startswith('oracle_') else codes[arm][lookup[ident]['index']]
                projected=original_codes if arm=='oracle_original' else project(torch.from_numpy(original_codes)).numpy()
                used=np.zeros((4,n,8),np.float32);used[:,st:st+20]=projected
                g=f[arm+'/'+ident]
                if (g['latent'].shape!=(4,n,8) or g['backbone'].shape!=(4,n,4,3)
                        or not np.array_equal(g['target'][:],used) or not np.isfinite(g['latent'][:]).all()
                        or not np.isfinite(g['backbone'][:]).all()):raise ValueError('Changed normalized target or output')
                if arm.startswith('oracle_'):
                    check=check_backbones(g['backbone'][:],oracle['new/'+ident+'/backbone'][:],q['fragment'][:],st,ident)
                    gap=float(np.max(abs(g['latent'][:]-oracle['new/'+ident+'/latent'][:])))
                    if arm=='oracle_original' and gap>1e-5:raise ValueError('Original latent replay failed')
                    controls.append(dict(arm=arm,target_id=ident,latent_max_abs=gap,**check))
                records.extend(raw_rows(g['backbone'][:],q['fragment'][:],st,arm,ident,row['family']))
            for arm in ('isolated','ablated'):
                records.extend(raw_rows(original[arm+'/'+ident+'/backbone'][:],q['fragment'][:],st,arm+'_unprojected',ident,row['family']))
    if len(m['controls'])!=8 or m['controls']!=controls:raise ValueError('Control log mismatch')
    summary={arm:dict(samples=sum(r['arm']==arm for r in records),valid=sum(r['arm']==arm and r['coarse_valid'] for r in records),
                      raw=sum(r['arm']==arm and r['raw_gate_passed'] for r in records)) for arm in ('oracle_original',*c['spec']['arms'],'isolated_unprojected','ablated_unprojected')}
    isolated=summary['isolated'];qualified=isolated['valid']>=8 and isolated['raw']>=2 and isolated['valid']>summary['isolated_unprojected']['valid']
    return dict(status='complete',qualified=qualified,context_normalization_profile=True,summary=summary,records=records,
                controls=controls,manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],
                elapsed_seconds=m['elapsed_seconds'],designability_tested=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/context_normalization_profile_protocol.json';spec=json.loads(protocol.read_text())
    source=root/spec['source_generation'];gm=json.loads((source/'manifest.json').read_text());parent=gm['config']
    c=dict(context_normalization_profile=True,parent=parent,spec=spec,
           selected=[next(r for r in parent['selected'] if r['bucket']==b) for b in (128,256,384,512)],sources=[],
           allocation_minutes=10,work_cap_seconds=480)
    for key,path in [('protocol',protocol),('source_manifest',source/'manifest.json'),('source_report',root/'reports'/(source.name+'.json')),('source_predictions',source/'predictions.h5')]:
        c[key]=str(path.resolve());c['sources'].append(dict(path=c[key],sha256=sha(path)))
    c['sources']+=parent['sources'];c['file_identity']=[identity(r['path']) for r in c['sources']]
    c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Four fixed families;48normalized outputs plus16exact replay controls')


if __name__=='__main__':main()
