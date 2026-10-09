"""Separate donor validity, query transfer, and unchanged oracle replay."""
import json
from pathlib import Path
import h5py
import numpy as np
from retrieved_context_profile import audit
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text())
    if m['status']!='complete':return dict(status='failed',qualified=False,error=m.get('error'))
    c=m['config'];parent=audit(c);path=run/'predictions.h5'
    if sha(path)!=m['predictions_sha256'] or m['training_updates_executed']!=0:raise ValueError('Changed output archive')
    arms=('oracle_original',*c['spec']['arms'],'donor_self')
    expected={(arm,r['id']) for arm in arms for r in c['selected']}
    if len(m['batches'])!=16 or {(r['arm'],r['target_id']) for r in m['batches']}!=expected:raise ValueError('Missing timing/output inventory')
    records=[];controls=[]
    with h5py.File(path) as f,h5py.File(c['inputs']) as inputs,h5py.File(c['library']) as library,h5py.File(c['oracle_predictions']) as oracle,h5py.File(c['fragments']) as queries:
        if set(f)!=set(arms):raise ValueError('Wrong profile groups')
        for arm in arms:
            if set(f[arm])!={r['id'] for r in c['selected']}:raise ValueError('Dropped query')
        for row in c['selected']:
            ident=row['id'];q=queries['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
            for arm in arms:
                name,n,offset,family,fragment=ident,row['length'],st,row['family'],q['fragment'][:]
                if arm=='oracle_original':target=oracle['new/'+ident+'/target'][:,st:st+20]
                elif arm=='donor_self':
                    donor=c['donors'][ident]['retrieved'][0];name,n,offset,family=donor['id'],donor['length'],donor['start'],donor['family']
                    target=inputs[ident+'/retrieved'][0]
                    fragment=library['train/'+name+'/reference_backbone'][offset:offset+20]
                else:target=inputs[ident+'/'+arm][:]
                used=np.zeros((4,n,8),np.float32);used[:,offset:offset+20]=target;g=f[arm+'/'+ident]
                if (g['latent'].shape!=(4,n,8) or g['backbone'].shape!=(4,n,4,3) or not np.array_equal(g['target'][:],used)
                        or not np.isfinite(g['latent'][:]).all() or not np.isfinite(g['backbone'][:]).all()):raise ValueError('Changed native code inputs or outputs')
                bb=g['backbone'][:]
                if arm=='oracle_original':
                    gap=float(np.max(abs(g['latent'][:]-oracle['new/'+ident+'/latent'][:])))
                    check=check_backbones(bb,oracle['new/'+ident+'/backbone'][:],fragment,offset,ident)
                    if gap>1e-5:raise ValueError('Oracle replay failed')
                    controls.append(dict(target_id=ident,latent_max_abs=gap,**check))
                records.extend(dict(r,query_id=ident,bucket=row['bucket']) for r in raw_rows(bb,fragment,offset,arm,name,family))
    if controls!=m['controls']:raise ValueError('Numerical control report differs')
    summary={arm:dict(samples=sum(r['arm']==arm for r in records),valid=sum(r['arm']==arm and r['coarse_valid'] for r in records),
                       raw=sum(r['arm']==arm and r['raw_gate_passed'] for r in records)) for arm in arms}
    qualified=(summary['retrieved']['valid']>=8 and summary['retrieved']['raw']>=2
               and summary['retrieved']['raw']>summary['random']['raw'] and summary['donor_self']['valid']>=8)
    return dict(status='complete',qualified=qualified,retrieved_context_profile=True,summary=summary,records=records,controls=controls,
                manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],elapsed_seconds=m['elapsed_seconds'],
                import_seconds=m['import_seconds'],phases=m['phases'],generation_seconds=sum(r['seconds'] for r in m['batches']),
                peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['batches']),designability_tested=False)
