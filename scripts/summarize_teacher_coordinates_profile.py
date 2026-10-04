"""Recompute parity from all saved atoms before accepting an efficiency change."""
import argparse
import json
import math
from pathlib import Path
import h5py
import numpy as np
from latentfold.metrics import ca_metrics
from teacher_coordinates_profile_core import audit, sha


def analyze(run):
    m = json.loads((run/'manifest.json').read_text()); p = audit(m['config'])
    if m['status'] != 'complete': return dict(status='failed', error=m.get('error', 'Incomplete profile'), qualified=False)
    expected = {(i, arm, repeat) for i in range(8) for arm in ('full', 'coordinates') for repeat in range(4)}
    actual = [(r['entry_index'], r['arm'], r['repeat']) for r in m['records']]
    if len(actual) != 64 or set(actual) != expected or not m['parameters_unchanged']:
        raise ValueError('Incomplete paired profile')
    if m['training_updates_executed'] or m['new_design_attempts']: raise ValueError('Unexpected scientific work')
    if any(not math.isfinite(r['seconds']) or r['seconds'] <= 0 for r in m['records']): raise ValueError('Invalid timings')
    parity = []; history = []
    with h5py.File(run/'coordinates.h5') as f, h5py.File(m['config']['parent_refolded']) as old:
        if set(f) != {str(i) for i in range(8)}: raise ValueError('Unexpected coordinate inventory')
        for i, entry in enumerate(m['config']['entries']):
            g = f[str(i)]; reference = g['full_0'][:]
            if not np.isfinite(reference).all(): raise ValueError('Nonfinite reference')
            if set(g) != {f'{a}_{r}' for a in ('full','coordinates') for r in range(4)} | {'backbone_indices'}:
                raise ValueError('Missing profile coordinates')
            for arm in ('full', 'coordinates'):
                for repeat in range(4):
                    coords = g[f'{arm}_{repeat}'][:]
                    if coords.shape != reference.shape or not np.isfinite(coords).all(): raise ValueError('Invalid coordinates')
                    parity.append(dict(entry_index=i, arm=arm, repeat=repeat,
                                       max_atom_difference=float(np.max(np.abs(coords-reference)))))
            bb = reference[0, g['backbone_indices'][:], :]
            previous = old[f"{entry['name']}/{entry['sequence_index']}"][:]
            history.append(dict(entry_index=i, **ca_metrics(previous[:,1], bb[:,1])))
    seconds = {}; memory = {}
    for arm in ('full','coordinates'):
        rows = [r for r in m['records'] if r['arm'] == arm and r['repeat'] > 0]
        seconds[arm] = sum(r['seconds'] for r in rows)
        memory[arm] = max(r['peak_allocated_bytes'] for r in rows)/2**30
    reduction = 1-seconds['coordinates']/seconds['full']; buckets = []
    for bucket in (128,256,384,512):
        totals = {arm:sum(r['seconds'] for r in m['records'] if r['arm']==arm and r['repeat']>0 and m['config']['entries'][r['entry_index']]['bucket']==bucket) for arm in ('full','coordinates')}
        buckets.append(dict(bucket=bucket,seconds=totals,reduction=1-totals['coordinates']/totals['full']))
    numerical = all(r['max_atom_difference'] <= p['max_atom_coordinate_difference'] for r in parity) and all(r['ca_rmsd'] <= p['historical_ca_rmsd_max'] and r['ca_lddt'] >= p['historical_ca_lddt_min'] for r in history)
    useful = reduction >= p['minimum_timed_seconds_reduction'] and all(r['reduction'] >= -p['maximum_bucket_seconds_regression'] for r in buckets)
    return dict(status='complete', qualified=numerical and useful, numerical_parity=numerical,
        timed_seconds=seconds, seconds_reduction=reduction, peak_allocated_gib=memory,
        buckets=buckets, parity=parity, historical_parity=history,
        manifest_sha256=sha(run/'manifest.json'), coordinates_sha256=sha(run/'coordinates.h5'),
        config=m['config'], elapsed_seconds=m['elapsed_seconds'],
        scope='Eight archived training sequences; 64 folds including warmups, 24 timed per arm. Same FP32 kernels, seeds and sampling settings. Confidence outputs unused by designability assay. Not a new accuracy or designability experiment.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1: raise ValueError('One matched profile required')
    d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Refolding without unused confidence outputs','',f"Qualified: {d['qualified']}."]
    if d['status']=='complete':
        lines += ['',f"Exact-settings coordinate parity: {d['numerical_parity']}. Timed GPU-worker reduction: {100*d['seconds_reduction']:.2f}%. Peak allocated GiB: {d['peak_allocated_gib']}.",'','| Length bucket | Seconds saved |','|---|---:|']
        lines += [f"|{r['bucket']}|{100*r['reduction']:.2f}%|" for r in d['buckets']]
        lines += ['',d['scope']]
    else: lines += ['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ('config','parity','historical_parity')}))


if __name__=='__main__': main()
