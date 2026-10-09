import argparse
import json
import math
from pathlib import Path
import h5py
import numpy as np
from teacher_concurrency_core import audit, sha


def decision(parity, reduction, buckets):
    return parity and reduction>=.10 and all(r['reduction']>=-.05 for r in buckets)


def analyze(run):
    m=json.loads((run/'manifest.json').read_text())
    if m.get('teacher_staging'):
        from teacher_staging import analyze as analyze_staging
        return analyze_staging(run)
    spec=audit(m['config'])
    if m['status']!='complete':return dict(status='failed',qualified=False,error=m.get('error'))
    wanted={(i,mode,r) for i in range(8) for mode in ('sequential','concurrent') for r in range(4)}
    if (len(m['records'])!=64 or {(r['entry_index'],r['mode'],r['repeat']) for r in m['records']}!=wanted
            or any(r['dataset']!=f"{r['entry_index']}/{r['mode']}_{r['repeat']}" for r in m['records'])
            or any(r['bucket']!=m['config']['original']['entries'][2*r['pair']]['bucket'] for r in m['pairs'])
            or len(m['pairs'])!=32 or {(r['pair'],r['mode'],r['repeat']) for r in m['pairs']}!={(i,mode,r) for i in range(4) for mode in ('sequential','concurrent') for r in range(4)}
            or not all(r['parameters_unchanged'] for r in m['records'])
            or m['training_updates_executed'] or m['new_design_attempts']
            or any(not math.isfinite(r['seconds']) or r['seconds']<=0 for r in m['pairs']+m['records'])
            or m['coordinates_sha256']!=sha(run/'coordinates.h5')):
        raise ValueError('Incomplete or changed concurrency profile')
    rm=json.loads(Path(m['config']['reference_manifest']).read_text())
    rng={r['entry_index']:r['rng_after'] for r in rm['records'] if r['arm']=='full' and r['repeat']==0}
    parity=[]
    with h5py.File(run/'coordinates.h5') as f,h5py.File(m['config']['reference_coordinates']) as ref:
        if set(f)!={str(i) for i in range(8)}:raise ValueError('Changed coordinate denominator')
        for i in range(8):
            if set(f[str(i)])!={mode+'_'+str(r) for mode in ('sequential','concurrent') for r in range(4)}:raise ValueError('Missing repeated coordinates')
        for r in m['records']:
            value=f[r['dataset']][:];old=ref[str(r['entry_index'])+'/full_0'][:]
            if value.shape!=old.shape or not np.isfinite(value).all():raise ValueError('Malformed full-atom coordinates')
            parity.append(dict(entry_index=r['entry_index'],mode=r['mode'],repeat=r['repeat'],max_atom_difference=float(np.max(np.abs(value-old))),rng_equal=r['rng_after']==rng[r['entry_index']]))
    seconds={mode:sum(r['seconds'] for r in m['pairs'] if r['mode']==mode and r['repeat']>0) for mode in ('sequential','concurrent')}
    reduction=1-seconds['concurrent']/seconds['sequential'];buckets=[]
    for b in (128,256,384,512):
        values={mode:sum(r['seconds'] for r in m['pairs'] if r['bucket']==b and r['mode']==mode and r['repeat']>0) for mode in seconds}
        buckets.append(dict(bucket=b,seconds=values,reduction=1-values['concurrent']/values['sequential']))
    numerical=all(r['max_atom_difference']<=spec['max_atom_difference'] and r['rng_equal'] for r in parity)
    return dict(status='complete',qualified=decision(numerical,reduction,buckets),numerical_parity=numerical,
        manifest_sha256=sha(run/'manifest.json'),coordinates_sha256=sha(run/'coordinates.h5'),timed_pair_seconds=seconds,
        seconds_reduction=reduction,buckets=buckets,parity=parity,elapsed_seconds=m['elapsed_seconds'],
        maximum_worker_reserved_gib=max(r['peak_reserved_bytes'] for r in m['records'])/2**30,
        scope='One assigned GPU, two private models and RNGs, unchangedFP32+fullconfidence,64folds of8archived sequences. Pair walltime includes dispatch and host transfer. Both workers resident in both modes. Pass licenses end-to-end pipeline validation only; not adoption or a scientific accuracy claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    # Preserve an already audited staging report's identity: downstream jobs
    # bind its bytes and metadata before allocating a GPU.
    target=a.output.with_suffix('.json');mp=a.runs[0]/'manifest.json'
    if target.exists() and a.output.with_suffix('.md').exists():
        old=json.loads(target.read_text());m=json.loads(mp.read_text())
        if (old.get('teacher_staging') and old['status']=='complete' and m['status']=='complete'
                and old['manifest_sha256']==sha(mp) and old['coordinates_sha256']==sha(a.runs[0]/'coordinates.h5')):
            from teacher_staging import audit as audit_staging
            audit_staging(m['config']);return
    d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    visible={k:v for k,v in d.items() if k!='parity'}
    title='Teacher checkpoint staging' if d.get('teacher_staging') else 'Concurrent refolding efficiency'
    a.output.with_suffix('.md').write_text('# '+title+'\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
