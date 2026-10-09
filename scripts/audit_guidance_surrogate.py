"""Join audited likelihood changes to actual fixed-budget refold outcomes.

This retrospective diagnostic neither selects samples nor changes advancement
gates. Repeated training families are not independent validation data.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import h5py

from prepare_overfit import sha
from gpu_real_utilization import analyze as analyze_utilization


def unique_index(rows, keys):
    result = {tuple(row[k] for k in keys): row for row in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate sample identity')
    return result


def covalent_summary(configs):
    """Descriptive bond distributions; these do not constitute a validity gate."""
    pooled = {}
    sources = {}
    for config, joint in configs:
        path = Path(config['predictions'])
        sources[str(path)] = sha(path)
        if sources[str(path)] != config['predictions_sha256']:
            raise ValueError('Changed raw backbone archive')
        with h5py.File(path, locking=False) as f:
            for row in config['entries']:
                arm = 'guided' if joint else (
                    'geometry' if row['arm'] == 'guided' else row['arm'])
                bb = f[row['dataset']][0]
                start = row['fixed_start']
                for region, x in [('chain', bb),
                                  ('motif', bb[start:start + len(row['fixed_sequence'])])]:
                    for name, a, b in (
                            ('N_CA', x[:, 0], x[:, 1]),
                            ('CA_C', x[:, 1], x[:, 2]),
                            ('C_O', x[:, 2], x[:, 3]),
                            ('C_N_next', x[:-1, 2], x[1:, 0]),
                            ('CA_CA_next', x[:-1, 1], x[1:, 1])):
                        pooled.setdefault((arm, region, name), []).append(
                            np.linalg.norm(a - b, axis=-1))
    return [dict(arm=arm, region=region, bond=name,
                 quantile01_50_99_A=np.quantile(np.concatenate(arrays), [.01, .5, .99]).tolist())
            for (arm, region, name), arrays in sorted(pooled.items())], sources


def analyze(root, refold_report):
    d = json.loads(refold_report.read_text())
    run = root / 'runs' / refold_report.stem
    manifest = run / 'manifest.json'
    m = json.loads(manifest.read_text())
    c = m['config']
    if (d['status'] != 'complete' or not d['sequence_guidance_refold']
            or d['manifest_sha256'] != sha(manifest)
            or d['refolded_sha256'] != sha(run / 'refolded.h5')):
        raise ValueError('Changed or incomplete refold evidence')
    paths = {k: Path(c[k]) for k in ('generation_report', 'baseline_refold_report')}
    for key, path in paths.items():
        if sha(path) != c[key + '_sha256']:
            raise ValueError('Changed source: ' + key)
    generation = json.loads(paths['generation_report'].read_text())
    old = json.loads(paths['baseline_refold_report'].read_text())
    old_manifest = Path(c['baseline_refold_manifest'])
    if sha(old_manifest) != c['baseline_refold_manifest_sha256']:
        raise ValueError('Changed baseline manifest')
    old_config = json.loads(old_manifest.read_text())['config']
    scores = unique_index(generation['sequence_scores'], ('arm', 'target_id', 'slot'))
    records = []
    for arm, source, source_arm in (
            ('baseline', old, 'baseline'), ('geometry', old, 'guided'),
            ('guided', d, 'guided')):
        for row in source['records']:
            if row['arm'] != source_arm:
                continue
            key = (arm, row['target_id'], row['generation_slot'])
            records.append(dict(
                arm=arm, target_id=row['target_id'], slot=row['generation_slot'],
                motif_nll=scores[key]['nll'], raw=bool(row['raw_gate_passed']),
                strict=bool(row['scaffold_joint_success']),
                designable=bool(row['valid_designable'])))
    index = unique_index(records, ('arm', 'target_id', 'slot'))
    if set(index) != set(scores) or len(index) != 48:
        raise ValueError('Missing or mismatched paired outcomes')
    summary = []
    families = sorted({row['target_id'] for row in records})
    if len(families) != 4:
        raise ValueError('Changed diagnostic panel')
    for arm in ('baseline', 'geometry', 'guided'):
        for family in [None] + families:
            selected = [row for row in records if row['arm'] == arm
                        and (family is None or row['target_id'] == family)]
            summary.append(dict(
                arm=arm, family=family, samples=len(selected),
                mean_motif_nll=float(np.mean([r['motif_nll'] for r in selected])),
                **{key: sum(r[key] for r in selected)
                   for key in ('raw', 'strict', 'designable')}))
    paired = []
    for row in records:
        if row['arm'] == 'guided':
            baseline = index['baseline', row['target_id'], row['slot']]
            paired.append(dict(
                target_id=row['target_id'], slot=row['slot'],
                nll_change=row['motif_nll'] - baseline['motif_nll'],
                strict_change=int(row['strict']) - int(baseline['strict']),
                designable_change=int(row['designable']) - int(baseline['designable'])))
    covalent, covalent_sources = covalent_summary([(old_config, False), (c, True)])
    utilization = analyze_utilization(root, run.name.rsplit('_', 1)[1])
    nvml = list(csv.reader((run / 'nvml.csv').read_text().splitlines()))
    if not nvml or any(row[1].strip() != utilization['uuid'] for row in nvml):
        raise ValueError('Unbound GPU memory samples')
    resources = dict(
        worker_seconds=m['elapsed_seconds'], utilization=utilization,
        peak_used_GiB=max(float(row[4]) for row in nvml) / 1024,
        total_GiB=float(nvml[0][5]) / 1024,
        new_sequence_refolds=128, reused_sequence_refolds=160)
    return dict(
        status='complete', summary=summary, paired=paired, records=records,
        covalent_bonds=covalent, resources=resources,
        improved_likelihood_pairs=sum(r['nll_change'] < 0 for r in paired),
        source_hashes={**covalent_sources, **{str(p): sha(p) for p in
                      [refold_report, old_manifest, *paths.values(), Path(__file__),
                       run / 'dcgm.txt', run / 'nvml.csv', run / 'device_metadata.json']}},
        scope='Retrospective, repeatedly used four-family training diagnostic. '
              'Likelihood is an optimized surrogate, not independent designability '
              'evidence. No new sequence attempts, changed gates, or training labels.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--refold-report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d = analyze(Path(__file__).resolve().parents[1], a.refold_report)
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2) + '\n')
    rows = [r for r in d['summary'] if r['family'] is None]
    lines = ['# Guidance surrogate audit', '', d['scope'], '',
             '| Arm | Mean motif NLL | Raw matches | Strict refold success | Designable |',
             '|---|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['arm']} | {r['mean_motif_nll']:.3f} | "
                     f"{r['raw']}/16 | {r['strict']}/16 | {r['designable']}/16 |")
    lines += ['', f"Joint guidance reduced motif NLL in {d['improved_likelihood_pairs']}/16 "
              'paired samples. Lower is better for NLL. Strict success requires '
              'the same valid refold to match the original motif, global fold, '
              'and scaffold; all failures remain in the denominator.', '']
    lines += ['The accompanying local JSON also reports chain and motif covalent-bond '
              'distributions (1st, 50th, 99th percentiles). These are descriptive, '
              'pooled-residue diagnostics, not a stereochemical validation or a new gate.', '']
    res = d['resources']
    util = res['utilization']
    lines += [f"One RTX; {res['worker_seconds']:.1f} worker seconds; "
              f"{res['peak_used_GiB']:.2f}/{res['total_GiB']:.2f} GiB peak/total device memory. "
              '128 new sequence refolds; 160 unchanged baseline/native attempts reused.', '']
    if util['status'] == 'complete':
        means = util['means']
        lines += [f"Captured weighted utilization: {util['real_utilization_percent']:.2f}% "
                  f"over {util['valid_samples']} complete one-second samples. "
                  f"SM {100 * means['sm_active']:.2f}%, tensor "
                  f"{100 * means['tensor_active']:.2f}%, DRAM "
                  f"{100 * means['dram_active']:.2f}%, graphics engine "
                  f"{100 * means['gr_engine_active']:.2f}%. "
                  'Excludes pre-recorder startup; not the dashboard 24-hour statistic. '
                  'Device memory occupancy is distinct from DRAM activity.', '']
    a.output.with_suffix('.md').write_text('\n'.join(lines))
    print(json.dumps(rows))


if __name__ == '__main__':
    main()
