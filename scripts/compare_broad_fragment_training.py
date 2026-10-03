"""Matched-draw audit for the prospectively declared data/objective factorial."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from prepare_overfit import sha
from profile_gpu import atomic_json


def compare_traces(manifests):
    fields = ('step', 'length', 'batch', 'learning_rate_factor', 'self_conditioned',
              'noise_sha256', 'time_sha256', 'drop_sha256', 'rng_sha256', 'global_rng_sha256')
    first = next(iter(manifests.values()))
    for m in manifests.values():
        if len(m['training']) != len(first['training']):
            raise ValueError('Unequal training exposure')
        for a, b in zip(first['training'], m['training']):
            if any(a[k] != b[k] for k in fields):
                raise ValueError('Unmatched random draws or schedule')
    for corpus in ('control512', 'broad'):
        rows = [m for m in manifests.values() if m['config']['corpus'] == corpus]
        if len(rows) != 2:
            raise ValueError('Both objectives required for each corpus')
        for a, b in zip(rows[0]['training'], rows[1]['training']):
            if a['ids'] != b['ids'] or a['conditions'] != b['conditions']:
                raise ValueError('Unmatched within-corpus target/condition draws')
    return len(first['training'])


def initial_parity(reference, candidate):
    count = 0
    with h5py.File(reference) as a, h5py.File(candidate) as b:
        def visit(name, value):
            nonlocal count
            if not isinstance(value, h5py.Dataset):
                if name not in b or set(value) != set(b[name]):
                    raise ValueError('Changed initial output inventory')
                return
            if name not in b or value.shape != b[name].shape:
                raise ValueError('Changed initial output shape')
            x, y = value[:], b[name][:]
            if not np.isfinite(x).all() or not np.isfinite(y).all() or np.max(abs(x-y)) > 1e-5:
                raise ValueError('Changed initial predictions')
            if name.endswith('/latent'):
                count += len(x)
        if set(a) != set(b):
            raise ValueError('Changed initial cohorts')
        a.visititems(visit)
    return count


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=Path, nargs=4, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = root / 'configs/fragment_broad_training_protocol.json'
    spec = json.loads(protocol.read_text())
    runs, manifests, reports, sources = {}, {}, {}, []
    for run in a.runs:
        mp, rp = run / 'manifest.json', root / 'reports' / (run.name + '.json')
        m, d = json.loads(mp.read_text()), json.loads(rp.read_text())
        c = m['config']; arm = c['extension_arm']
        if (m['status'] != 'complete' or d['status'] != 'complete'
                or d['manifest_sha256'] != sha(mp) or c['extension_protocol_sha256'] != sha(protocol)
                or arm in manifests or arm not in spec['arms']
                or (c['profile_only'] and not d['profile_qualified'])):
            raise ValueError('Unqualified or duplicate training arm')
        runs[arm], manifests[arm], reports[arm] = run, m, d
        sources.append(dict(run=str(run.resolve()), manifest_sha256=sha(mp), report_sha256=sha(rp)))
    if set(manifests) != set(spec['arms']) or len({m['config']['profile_only'] for m in manifests.values()}) != 1:
        raise ValueError('Incomplete or mixed factorial comparison')
    updates = compare_traces(manifests)
    first = next(iter(runs.values()))
    controls = {arm: initial_parity(first / 'evaluation_0.h5', run / 'evaluation_0.h5') for arm, run in runs.items()}
    result = dict(status='complete', matched_training_updates=updates, initial_predictions=controls,
                  profile_only=next(iter(manifests.values()))['config']['profile_only'],
                  protocol_sha256=sha(protocol), sources=sources,
                  arms={arm: {k: d[k] for k in ('training_seconds', 'evaluation_seconds', 'elapsed_seconds',
                                                'max_reserved_GiB', 'total_training_updates', 'summaries')} for arm, d in reports.items()})
    atomic_json(a.output.with_suffix('.json'), result)
    short = {k: v for k, v in result.items() if k != 'arms'}
    a.output.with_suffix('.md').write_text('# Matched broader fragment training\n\n```json\n' + json.dumps(short, indent=2) + '\n```\n')
    print(json.dumps({k: result[k] for k in ('status', 'matched_training_updates', 'initial_predictions')}))


if __name__ == '__main__':
    main()
