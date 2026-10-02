"""Describe existing native failures without filtering samples or changing gates."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np


LIMITS = {
    'peptide_outlier_fraction': .05,
    'ca_clashing_residue_fraction': .01,
    'ca_gap_fraction': .01,
}


def analyze(path):
    m = json.loads(path.read_text())
    if m['status'] != 'complete':
        raise ValueError('only completed native evaluations')
    c = m['config']
    selection = Path(c['selection'])
    if hashlib.sha256(selection.read_bytes()).hexdigest() != c['selection_sha256']:
        raise ValueError('selection changed')
    targets = {r['id']: r for r in json.loads(selection.read_text())['tuning']}
    if len(targets) != 64 or len({r['family'] for r in targets.values()}) != 64:
        raise ValueError('expected fixed64-family native panel')
    rows = m['scores']
    settings = {(r['head'], r['guidance']) for r in rows}
    keys = {(r['head'], r['guidance'], r['target_id'], r['sample']) for r in rows}
    expected = {(h, g, i, k) for h, g in settings for i in targets for k in range(3)}
    if keys != expected or len(rows) != len(expected) or ('original', 2) not in settings:
        raise ValueError('incomplete, duplicated, or wrong sample coverage')
    for r in rows:
        if any(not np.isfinite(r[k]) or not 0 <= r[k] <= 1 for k in LIMITS):
            raise ValueError('invalid geometry fraction')
        if bool(r['coarse_valid']) != all(r[k] <= v for k, v in LIMITS.items()):
            raise ValueError('geometry gate identity differs')
    baseline = {(r['target_id'], r['sample']) for r in rows
                if r['head'] == 'original' and r['guidance'] == 2 and not r['coarse_valid']}
    result = dict(manifest=str(path), manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  step=c['training_checkpoint_step'], heads={})
    for h, g in sorted(settings):
        group = [r for r in rows if (r['head'], r['guidance']) == (h, g)]
        bad = [r for r in group if not r['coarse_valid']]
        badkeys = {(r['target_id'], r['sample']) for r in bad}
        counts = Counter(r['target_id'] for r in bad)
        result['heads'][f'{h}_cfg{g}'] = dict(
            samples=len(group), invalid=len(bad), affected_families=len(counts),
            all_three_invalid=sum(n == 3 for n in counts.values()),
            causes={k: sum(r[k] > v for r in group) for k, v in LIMITS.items()},
            newly_invalid_vs_original=len(badkeys - baseline),
            recovered_vs_original=len(baseline - badkeys),
            failed_families=[dict(id=i, family=targets[i]['family'], length=targets[i]['length'],
                                  invalid=n, ca_lddt_mean=float(np.mean([r['ca_lddt'] for r in group if r['target_id'] == i])))
                             for i, n in sorted(counts.items())],
        )
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', nargs='+', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    results = [analyze(run / 'manifest.json') for run in a.runs]
    lines = ['# Native geometry failure diagnostic', '',
             'Descriptive analysis of completed tuning-panel samples. All64 families and all3 samples per head remain in the denominator. No filtering, repair, reweighting, threshold change, or new qualification. Cause counts overlap; coarse validity is not a physical certificate.', '']
    for d in results:
        lines += [f"## {Path(d['manifest']).parent.name}, checkpoint{d['step']}", '',
                  '| Head | Invalid /192 | Families affected | Families with all3 invalid | Peptide | CA clashes | CA gaps | Newly invalid / recovered vs original |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|']
        for name, r in d['heads'].items():
            counts = [r['causes'][k] for k in LIMITS]
            lines.append(f"| {name} | {r['invalid']} | {r['affected_families']} | {r['all_three_invalid']} | {counts[0]} | {counts[1]} | {counts[2]} | {r['newly_invalid_vs_original']} / {r['recovered_vs_original']} |")
        lines += ['', 'Affected families (invalid samples/3; length):', '']
        for name, r in d['heads'].items():
            values = ', '.join(f"{v['id']} ({v['invalid']}/3; L={v['length']})" for v in r['failed_families'])
            lines.append(f'- {name}: {values or "none"}.')
        lines.append('')
    lines += ['Equal aggregate validity need not mean the same structures fail. These paired counts distinguish persistent failures from newly introduced failures. Three draws cannot establish per-family retry probabilities; filtering existing samples would define a different pipeline and would require complete cost and no-output accounting. This diagnostic does not authorize bypassing the frozen native gate.']
    a.output.with_suffix('.json').write_text(json.dumps(results, indent=2) + '\n')
    a.output.with_suffix('.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
