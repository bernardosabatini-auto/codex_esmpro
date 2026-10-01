"""Compare matched training arms at a fully evaluated, predeclared checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def comparison(left, right):
    delta = np.asarray(left) - np.asarray(right)
    means = np.random.default_rng(20261001).choice(delta, (10000, len(delta)), replace=True).mean(1)
    return dict(candidate_mean=float(np.mean(left)), reference_mean=float(np.mean(right)),
                difference=float(delta.mean()), ci95=np.quantile(means, [.025, .975]).tolist())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, nargs="+", required=True)
    p.add_argument('--control', choices=('reference','cached_reference'), default='reference')
    p.add_argument('--step', type=int, choices=(500, 2000), required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    metrics = ('ca_lddt', 'tm_after_kabsch', 'coarse_valid')
    arms = {}; source_hashes = {}; selection_hashes = set()
    for run in a.runs:
        path = run / 'manifest.json'; raw = path.read_bytes(); m = json.loads(raw)
        if m['status'] not in ('running', 'complete') or m['updates'] < a.step:
            raise ValueError('requested checkpoint not available')
        arm = m['config']['arm']
        if arm in arms:
            raise ValueError('duplicate arm')
        source_hashes[str(path)] = hashlib.sha256(raw).hexdigest()
        selection_path = Path(m['config']['selection']); selection_raw = selection_path.read_bytes()
        if hashlib.sha256(selection_raw).hexdigest() != m['config']['selection_sha256']:
            raise ValueError('selection changed')
        selection_hashes.add(m['config']['selection_sha256'])
        tuning = json.loads(selection_raw)['tuning']; ids = sorted(r['id'] for r in tuning)
        if len(ids) != 64 or len({r['family'] for r in tuning}) != 64:
            raise ValueError('expected 64 unique tuning families')
        arms[arm] = {}
        for step in (0, a.step):
            rows = [r for r in m['scores'] if r['step'] == step]
            if len(rows) != 192 or {r['target_id'] for r in rows} != set(ids):
                raise ValueError('incomplete checkpoint evaluation')
            if any(sorted(r['sample'] for r in rows if r['target_id'] == i) != [0, 1, 2] for i in ids):
                raise ValueError('invalid sampling replication')
            arms[arm][step] = {key: [float(np.mean([r[key] for r in rows if r['target_id'] == i])) for i in ids] for key in metrics}
    expected = {'raw_reference','reference','empirical','balanced'} if a.control == 'reference' else {'cached_reference','cached_aligned_empirical'}
    if set(arms) != expected or len(selection_hashes) != 1:
        raise ValueError('unmatched arm selection')
    for arm in arms:
        for key in metrics:
            if not np.allclose(arms[arm][0][key], arms[a.control][0][key], atol=2e-5, rtol=0):
                raise ValueError('initial predictions differ across matched arms')
    results = {}
    for arm in arms:
        results[arm] = {baseline: {key: comparison(arms[arm][a.step][key], arms[a.control][step][key]) for key in metrics}
                        for baseline, step in [('initial', 0), ('matched_reference', a.step)]}
    d = dict(status='complete', step=a.step, control=a.control, source_manifest_sha256=source_hashes, comparisons=results,
             scope='64 tuning families, three samples each; single training seed. TM is after Kabsch, not TM-align optimization. No ensemble promotion claim.')
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2) + '\n')
    lines = [f'# Matched training at {a.step} updates', '', d['scope'], '']
    for key in metrics:
        lines += [f'## {key}', '', '| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |', '|---|---:|---:|---|---:|---|']
        for arm, result in results.items():
            x, y = result['initial'][key], result['matched_reference'][key]
            lines.append(f"| {arm} | {x['candidate_mean']:.5f} | {x['difference']:+.5f} | [{x['ci95'][0]:+.5f}, {x['ci95'][1]:+.5f}] | {y['difference']:+.5f} | [{y['ci95'][0]:+.5f}, {y['ci95'][1]:+.5f}] |")
        lines.append('')
    lines += ['AFDB reference coordinates are predictions. Evaluate state coverage and validity separately on the frozen development ensemble panel before any replication or promotion. Reserved confirmation and original test remain unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
