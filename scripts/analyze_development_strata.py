"""Secondary accuracy diagnostics by length and inherited CA continuity.

These exploratory strata do not change the preregistered pilot promotion rule.
Average inference samples, then training seeds, before resampling proteins.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import means_by_target, validate_scores


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--external', type=Path)
    p.add_argument('--pilots', nargs='*', type=Path, default=[])
    p.add_argument('--clusters', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    ref = json.loads((a.reference/'scores.json').read_text())
    manifest = json.loads((a.reference/'manifest.json').read_text())
    validate_scores(manifest, ref)
    setting = 'steps25_cfg2'
    metrics = ('tm_fixed_reference', 'ca_lddt')
    reference = {m: means_by_target(ref['records'], setting, m) for m in metrics}
    ids = set(reference[metrics[0]])
    metadata = {}
    for row in ref['records']:
        value = (row['length'], row['reference_adjacent_short_count'])
        if row['target_id'] in metadata and metadata[row['target_id']] != value:
            raise ValueError('reference metadata differs across samples')
        metadata[row['target_id']] = value
    clusters = json.loads(a.clusters.read_text())['clusters']
    if set(clusters) != ids:
        raise ValueError('cluster coverage differs')
    # PDB-entry resampling is a secondary check for correlated chains.
    entries = {name: name.split('_')[0].lower() for name in ids}
    candidates = {'untouched_pair': reference}
    if a.external:
        em = json.loads((a.external/'manifest.json').read_text())
        es = json.loads((a.external/'scores.json').read_text())
        keys = [(r['target_id'], r['sample']) for r in es['records']]
        expected = {(name, k) for name in ids for k in range(3)}
        if em['status'] != 'complete' or es['status'] != 'complete' or len(keys) != len(expected) or set(keys) != expected:
            raise ValueError('external results incomplete')
        if es['usalign'] != ref['usalign']:
            raise ValueError('external scoring executable/protocol differs')
        candidates['esmfold2_fast'] = {m: means_by_target(es['records'], 'esmfold2_steps50_loops3', m) for m in metrics}
    groups = {}
    for run in a.pilots:
        train = json.loads((run/'training.json').read_text())
        pm = json.loads((run/'evaluation/manifest.json').read_text())
        ps = json.loads((run/'evaluation/scores.json').read_text())
        validate_scores(pm, ps)
        if train['status'] != 'complete' or ps['usalign'] != ref['usalign']:
            raise ValueError('pilot training or scoring protocol invalid')
        key = (train['task']['seed'], train['task']['arm'])
        if key in groups:
            raise ValueError('duplicate training seed/arm')
        groups[key] = {m: means_by_target(ps['records'], setting, m) for m in metrics}
    for arm in sorted({arm for _, arm in groups}):
        members = [value for (seed, name), value in groups.items() if name == arm]
        if len(members) != 3:
            raise ValueError('expected three training seeds per arm')
        candidates[arm] = {m: {name: float(np.mean([v[m][name] for v in members])) for name in ids} for m in metrics}
    strata = {'all': sorted(ids)}
    for lo, hi in ((0, 128), (128, 256), (256, 384), (384, 512)):
        strata[f'length_{lo+1}_{hi}'] = sorted(n for n, (length, _) in metadata.items() if lo < length <= hi)
    for discontinuous in (False, True):
        strata['reference_CA_breaks' if discontinuous else 'reference_CA_continuous'] = sorted(
            n for n, (length, adjacent) in metadata.items() if (adjacent < length-1) == discontinuous)
    comparisons = [('untouched_pair', n) for n in candidates if n != 'untouched_pair']
    for candidate in ('geometry','confidence'):
        if candidate in candidates and 'flow' in candidates:
            comparisons.append(('flow', candidate))
    result = dict(status='complete',diagnostic_only=True, comparisons={})
    lines = ['# Development accuracy diagnostics', '',
             'Exploratory strata; no multiplicity correction and no change to the primary promotion gate. All inference samples are averaged per target; pilot results also average the three training seeds. These confidence intervals are conditional on those seeds.', '',
             'Reference CA breaks are a coordinate proxy, not verified residue maps or domain labels.', '',
             '| Comparison (second minus first) | Stratum | Targets | Mean TM change | 95% sequence-cluster CI |',
             '|---|---|---:|---:|---|']
    for first, second in comparisons:
        key = f'{second}_minus_{first}'; result['comparisons'][key] = {}
        for label, names in strata.items():
            if not names:
                continue
            scores = {m: paired_comparison({n:candidates[first][m][n] for n in names},
                {n:candidates[second][m][n] for n in names}, clusters={n:clusters[n] for n in names}) for m in metrics}
            result['comparisons'][key][label] = scores
            tm = scores['tm_fixed_reference']; low, high = tm['ci95']
            lines.append(f'| {key} | {label} | {len(names)} | {tm["theirs_minus_ours"]:+.5f} | [{low:+.5f}, {high:+.5f}] |')
        result['comparisons'][key]['all_entry_bootstrap'] = {m: paired_comparison(candidates[first][m], candidates[second][m], clusters=entries) for m in metrics}
    a.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    main()
