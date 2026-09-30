"""Judge hybrid inference against the saved strict-FP32 reference, including failures."""
import argparse
import json
from pathlib import Path

from latentfold.metrics import paired_comparison
from summarize_comparison import atomic_text, hardware, means_by_target, validate_scores


def analyze(runs, references, output):
    refs = {}
    for directory in references:
        m = json.loads((directory/'manifest.json').read_text())
        s = json.loads((directory/'scores.json').read_text())
        validate_scores(m, s)
        if m['precision'] != {'flow_precision': 'fp32', 'decoder_precision': 'fp32'}:
            raise ValueError('reference is not strict FP32')
        refs[m['model']] = (m, s)
    rows = []
    for run in runs:
        if not (run/'manifest.json').exists():
            rows.append(dict(run=str(run), status='missing_manifest', eligible=False))
            continue
        m = json.loads((run/'manifest.json').read_text())
        row = dict(run=str(run), model=m['model'], policy=m['precision']['flow_precision'],
                   collection_status=m['status'], controls=m['controls'], eligible=False)
        rows.append(row)
        if m['status'] != 'complete':
            row.update(status='rejected_or_incomplete', error=m.get('error', 'job ended before collection completed'))
            continue
        s = json.loads((run/'scores.json').read_text())
        settings = validate_scores(m, s)
        if settings != ['steps25_cfg2']:
            raise ValueError('hybrid experiment must use only 25 steps / guidance 2')
        ref, ref_scores = refs[m['model']]
        for key in ['checkpoint', 'dataset', 'decoder_checkpoint']:
            if m[key] != ref[key]:
                raise ValueError(f'changed {key}')
        for key in ['seed', 'samples', 'target_ids', 'target_manifest_sha256', 'decoder_steps', 'models']:
            if m['config'][key] != ref['config'][key]:
                raise ValueError(f'changed reference configuration {key}')
        if s['usalign'] != ref_scores['usalign']:
            raise ValueError('changed scoring executable')
        if len(m['controls']) != len(ref['controls']):
            raise ValueError('missing batch controls')
        setting = settings[0]
        delta = {}
        for metric in ['tm_fixed_reference', 'ca_lddt']:
            delta[metric] = paired_comparison(means_by_target(ref_scores['records'], setting, metric),
                                               means_by_target(s['records'], setting, metric))
        for metric in ['predicted_ca_gaps_on_reference_short', 'peptide_length_outliers_on_reference_short']:
            def normalized(records):
                return [dict(r, fraction=r[metric]/max(1, r['reference_adjacent_short_count'])) for r in records]
            delta[metric] = paired_comparison(means_by_target(normalized(ref_scores['records']), setting, 'fraction'),
                                               means_by_target(normalized(s['records']), setting, 'fraction'))
        seconds = sum(b['seconds_including_input_and_d2h'] for b in m['batches'])
        reference_seconds = sum(b['seconds_including_input_and_d2h'] for b in ref['batches'] if b['setting'] == setting)
        accuracy_pass = all(delta[k]['ci95'][0] >= -.005 for k in ['tm_fixed_reference', 'ca_lddt'])
        geometry_pass = all(delta[k]['ci95'][1] <= .001 for k in ['predicted_ca_gaps_on_reference_short', 'peptide_length_outliers_on_reference_short'])
        controls_pass = all(c['ca_rmsd'] <= .2 and c['ca_lddt'] >= .99 and c['reference_ca_lddt_absolute_change'] <= .005 for c in m['controls'])
        row.update(status='complete', paired=delta, accuracy_pass=accuracy_pass, geometry_pass=geometry_pass,
                   controls_pass=controls_pass, eligible=accuracy_pass and geometry_pass and controls_pass,
                   speedup_cached_pipeline=reference_seconds/seconds, seconds=seconds,
                   predictions_per_second=m['completed_predictions']/seconds,
                   accuracy=s['summaries'][setting],
                   peak_allocated_gib=max(b['peak_allocated_bytes'] for b in m['batches'])/2**30,
                   peak_reserved_gib=max(b['peak_reserved_bytes'] for b in m['batches'])/2**30,
                   hardware=hardware(Path(str(run)+'_nsight.sqlite'), m['batches']))
    result = dict(status='complete', rows=rows,
                  rule='Batch RMSD <=0.2 A, self CA lDDT >=0.99, native CA lDDT absolute change <=0.005. Paired target-bootstrap TM and CA lDDT lower 95% CI >=-0.005; geometry outlier fraction upper delta CI <=0.001.',
                  scope='Exploratory development-set precision selection; same cached embeddings/weights/noise. No homology clusters; no end-to-end ESMC speed claim.')
    lines = ['# Hybrid precision experiment', '', result['rule'], '', result['scope'], '',
             '| Model | Policy | Status | Eligible | Cached-pipeline speedup | TM change (95% CI) |',
             '|---|---|---|---|---:|---|']
    for r in rows:
        d = r.get('paired', {}).get('tm_fixed_reference')
        estimate = f"{d['theirs_minus_ours']:.5f} [{d['ci95'][0]:.5f}, {d['ci95'][1]:.5f}]" if d else 'not collected'
        speed = f"{r['speedup_cached_pipeline']:.2f}x" if 'speedup_cached_pipeline' in r else '—'
        lines.append(f"| {r.get('model', 'unknown')} | {r.get('policy', 'unknown')} | {r['status']} | {r['eligible']} | {speed} | {estimate} |")
    for r in rows:
        if r.get('error'):
            lines += ['', f"Failure for {r.get('model')} / {r.get('policy')}: {r['error']}", '']
    lines += ['', '## Hardware activity and memory', '',
              'SM activity includes waiting warps and is not peak FLOP utilization. Whole-capture counters include model loading and controls, but exclude subsequent profiler export. Memory is the maximum measured across collection batches.', '',
              '| Model / policy | SM active % | SM issue % | Tensor active % | Allocated / reserved GiB |',
              '|---|---:|---:|---:|---:|']
    for r in rows:
        if r['status'] == 'complete':
            h = r['hardware']['whole_capture_mean_percent']
            lines.append(f"| {r['model']} / {r['policy']} | {h['SMs Active [Throughput %]']:.1f} | {h['SM Issue [Throughput %]']:.1f} | {h['Tensor Active [Throughput %]']:.1f} | {r['peak_allocated_gib']:.1f} / {r['peak_reserved_gib']:.1f} |")
    lines += ['', 'A policy is eligible only when every declared gate passes. Eligibility is a development-set finding, not a validated final-test or training improvement.', '']
    atomic_text(output.with_suffix('.json'), json.dumps(result, indent=2, allow_nan=False)+'\n')
    atomic_text(output.with_suffix('.md'), '\n'.join(lines))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', nargs='+', type=Path, required=True)
    p.add_argument('--references', nargs=2, type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    r = analyze(a.runs, a.references, a.output)
    print(json.dumps({'status': r['status'], 'eligible': sum(x['eligible'] for x in r['rows']), 'report': str(a.output.with_suffix('.md'))}))


if __name__ == '__main__':
    main()
