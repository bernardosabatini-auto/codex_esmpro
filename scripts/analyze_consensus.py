"""Freeze native-free sample choices, then evaluate them on reused development data."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import h5py
import numpy as np
from latentfold.metrics import paired_comparison
from latentfold.selection import ca_lddt_medoid
from summarize_comparison import validate_scores


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def select(run, output, protocol):
    if output.exists():
        raise FileExistsError(output)
    manifest = json.loads((run/'manifest.json').read_text())
    config = manifest['config']
    if manifest['status'] != 'complete' or config['samples'] != 3:
        raise ValueError('incomplete three-sample run')
    setting = 'steps25_cfg2'
    rows = {}
    started = time.monotonic()
    with h5py.File(run/'predictions.h5', 'r') as predictions:
        for target in predictions[setting].values():
            name = target.attrs['target_id']
            if name in rows or set(target) != {'0', '1', '2'}:
                raise ValueError('duplicate target or sample coverage mismatch')
            sample, confidence, matrix = ca_lddt_medoid([target[str(k)]['ca'][:] for k in range(3)])
            rows[name] = dict(sample=sample, agreement=confidence, pairwise=matrix)
    if set(rows) != set(config['target_ids']):
        raise ValueError('target coverage mismatch')
    result = dict(status='complete', policy='ca_lddt_medoid_v1', run=str(run.resolve()),
                  setting=setting, protocol_sha256=digest(protocol), manifest_sha256=digest(run/'manifest.json'),
                  predictions_sha256=digest(run/'predictions.h5'), selection_seconds=time.monotonic()-started,
                  choices=rows, note='Choices frozen before opening native score files; no native coordinates used.')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'choices'}, indent=2))


def evaluate(selection, clusters_path, output):
    choices = json.loads(selection.read_text()); run = Path(choices['run'])
    if digest(run/'manifest.json') != choices['manifest_sha256'] or digest(run/'predictions.h5') != choices['predictions_sha256']:
        raise ValueError('prediction inputs changed after choice')
    manifest = json.loads((run/'manifest.json').read_text())
    scores = json.loads((run/'scores.json').read_text()); validate_scores(manifest, scores)
    rows = {}
    for row in scores['records']:
        if row['setting'] == choices['setting']:
            rows.setdefault(row['target_id'], {})[row['sample']] = row
    clusters = json.loads(clusters_path.read_text())['clusters']
    if set(rows) != set(choices['choices']) or set(clusters) != set(rows):
        raise ValueError('evaluation target coverage mismatch')
    metrics = ('tm_fixed_reference', 'ca_lddt')
    paired = {}
    selected_rows = {name:samples[choices['choices'][name]['sample']] for name, samples in rows.items()}
    for metric in metrics:
        selected = {name:row[metric] for name,row in selected_rows.items()}
        baselines = dict(first_sample={name:samples[0][metric] for name,samples in rows.items()},
                         sample_mean={name:float(np.mean([r[metric] for r in samples.values()])) for name,samples in rows.items()})
        paired[metric] = {name:paired_comparison(values, selected, clusters=clusters) for name, values in baselines.items()}
    oracle = {name:max(r['tm_fixed_reference'] for r in samples.values()) for name,samples in rows.items()}
    mean_tm = {name:float(np.mean([r['tm_fixed_reference'] for r in samples.values()])) for name,samples in rows.items()}
    geometry = {}
    for key in ('predicted_ca_gaps_on_reference_short', 'peptide_length_outliers_on_reference_short'):
        selected = sum(row[key] for row in selected_rows.values())
        mean = sum(float(np.mean([r[key] for r in samples.values()])) for samples in rows.values())
        geometry[key] = dict(selected_total=selected, sample_mean_total=mean, difference=selected-mean)
    tm = paired['tm_fixed_reference']['sample_mean']
    eligible = (tm['theirs_minus_ours'] >= .002 and tm['ci95'][0] > 0
                and paired['tm_fixed_reference']['first_sample']['theirs_minus_ours'] >= 0
                and paired['ca_lddt']['sample_mean']['theirs_minus_ours'] >= 0)
    result = dict(status='complete', selection_sha256=digest(selection), scores_sha256=digest(run/'scores.json'),
        clusters_sha256=digest(clusters_path), pairs=paired, geometry=geometry,
        oracle_tm_only=paired_comparison(mean_tm, oracle, clusters=clusters), eligible_for_noise_replication=eligible,
        selection_seconds=choices['selection_seconds'], diagnostic_only=True)
    output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    lines = ['# Reference-free three-sample selection', '', choices['note'], '',
        'Exploratory diagnostic on 626 reused development proteins. Select the CA lDDT medoid of three predictions, with no native input and no fitted coefficients. This uses three generated samples per selected prediction.', '',
        '| Metric | Baseline | Selected | Change [95% cluster CI] |', '|---|---:|---:|---|']
    for metric in metrics:
        for name, row in paired[metric].items():
            lines.append(f"| {metric}, {name} | {row['ours']:.5f} | {row['theirs']:.5f} | {row['theirs_minus_ours']:+.5f} {row['ci95']} |")
    lines += ['', f"Eligible for independent inference-noise replication: {eligible}. No final-test targets scored.", '',
        'Native-TM best-of-three is an oracle upper bound only: '+str(result['oracle_tm_only']['theirs'])+'. It is not the selected model accuracy.', '',
        '```json', json.dumps(result, indent=2), '```']
    output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='phase', required=True)
    choose = sub.add_parser('select')
    choose.add_argument('--run', type=Path, required=True)
    choose.add_argument('--output', type=Path, required=True)
    choose.add_argument('--protocol', type=Path, required=True)
    score = sub.add_parser('evaluate')
    score.add_argument('--selection', type=Path, required=True)
    score.add_argument('--clusters', type=Path, required=True)
    score.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.phase == 'select':
        select(args.run, args.output, args.protocol)
    else:
        evaluate(args.selection, args.clusters, args.output)


if __name__ == '__main__':
    main()
