"""Validate completed comparisons and produce paired accuracy/cost reports on CPU."""
import argparse
from bisect import bisect_right
from collections import defaultdict
import json
from pathlib import Path
import sqlite3

import numpy as np
from latentfold.metrics import paired_comparison

COUNTERS = ['SMs Active [Throughput %]', 'SM Issue [Throughput %]',
            'Tensor Active [Throughput %]', 'DRAM Read Bandwidth [Throughput %]',
            'DRAM Write Bandwidth [Throughput %]']


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text)
    temp.replace(path)


def validate_scores(manifest, scores):
    if manifest['status'] != 'complete' or scores['status'] != 'complete':
        raise ValueError('incomplete collection or scoring')
    config = manifest['config']
    settings = {f'steps{s}_cfg{g:g}' for s in config['flow_steps'] for g in config['guidance']}
    expected = {(s, t, k) for s in settings for t in config['target_ids']
                for k in range(config['samples'])}
    actual = [(r['setting'], r['target_id'], r['sample']) for r in scores['records']]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError('duplicate, missing or unexpected target/sample/setting')
    if len(actual) != manifest['completed_predictions']:
        raise ValueError('prediction count differs from manifest')
    values = np.array([[r['tm_fixed_reference'], r['ca_lddt']] for r in scores['records']])
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError('invalid accuracy metrics')
    return sorted(settings)


def hardware(trace, batches, *, prefix='collect::'):
    # Only call after Slurm termination / Nsight export, never on a live database.
    con = sqlite3.connect(trace.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        catalog = con.execute('select typeId,metricId,metricName from TARGET_INFO_GPU_METRICS').fetchall()
        chosen = {mid: name for _, mid, name in catalog if name in COUNTERS}
        types = {kind for kind, _, name in catalog if name in COUNTERS}
        if set(chosen.values()) != set(COUNTERS) or len(types) != 1:
            raise ValueError('missing or ambiguous hardware counters')
        ranges = con.execute("select start,end,text from NVTX_EVENTS where text like ? order by start", (prefix+'%',)).fetchall()
        if len({r[2] for r in ranges}) != len(ranges) or {r[2] for r in ranges} != {r['nvtx_range'] for r in batches}:
            raise ValueError('hardware intervals differ from collected batches')
        if not ranges or any(e is None or e <= s for s, e, _ in ranges):
            raise ValueError('invalid hardware intervals')
        if any(ranges[i][1] > ranges[i+1][0] for i in range(len(ranges)-1)):
            raise ValueError('overlapping hardware intervals')
        starts = [r[0] for r in ranges]
        total, by_range = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        first, last, count = None, None, 0
        sm_id = next(k for k, v in chosen.items() if v == COUNTERS[0])
        query = 'select timestamp,metricId,value from GPU_METRICS where typeId=? and metricId in (' + ','.join('?' for _ in chosen) + ')'
        for tick, mid, value in con.execute(query, [next(iter(types)), *chosen]):
            if not 0 <= value <= 100:
                raise ValueError('invalid hardware percentage')
            total[mid][0] += value
            total[mid][1] += 1
            if mid == sm_id:
                first = tick if first is None else min(first, tick)
                last = tick if last is None else max(last, tick)
                count += 1
            i = bisect_right(starts, tick)-1
            if i >= 0 and tick < ranges[i][1]:
                by_range[i, mid][0] += value
                by_range[i, mid][1] += 1
        if count < 2:
            raise ValueError('insufficient counter samples')
        period = (last-first)/(count-1)
        for i, (s, e, name) in enumerate(ranges):
            coverage = min(by_range[i, mid][1] for mid in chosen)*period/(e-s)
            if not .95 <= coverage <= 1.05:
                raise ValueError(f'incomplete counter coverage: {name}: {coverage}')
        return {
            'whole_capture_mean_percent': {chosen[k]: s/n for k, (s, n) in total.items()},
            'collection_mean_percent': {chosen[k]: sum(by_range[i, k][0] for i in range(len(ranges)))/sum(by_range[i, k][1] for i in range(len(ranges))) for k in chosen},
            'capture_seconds': (last-first)/1e9,
            'collection_seconds': sum(e-s for s, e, _ in ranges)/1e9,
            'counter_period_ns': period, 'validated_intervals': len(ranges),
            'caveat': 'SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection.'}
    finally:
        con.close()


def means_by_target(records, setting, metric):
    groups = defaultdict(list)
    for r in records:
        if r['setting'] == setting:
            groups[r['target_id']].append(r[metric])
    return {k: float(np.mean(v)) for k, v in groups.items()}


def analyze(runs, output):
    models = {}
    comparison_signature = None
    for run in runs:
        manifest = json.loads((run/'manifest.json').read_text())
        scores = json.loads((run/'scores.json').read_text())
        settings = validate_scores(manifest, scores)
        signature = (manifest['config'], manifest['dataset'], manifest['decoder_checkpoint'], manifest['precision'], scores['usalign'])
        if comparison_signature is not None and signature != comparison_signature:
            raise ValueError('comparison provenance/settings mismatch')
        comparison_signature = signature
        model = manifest['model']
        if model in models:
            raise ValueError('duplicate model')
        timings = {}
        for setting in settings:
            batches = [b for b in manifest['batches'] if b['setting'] == setting]
            n = scores['summaries'][setting]['predictions']
            if sum(b['batch'] for b in batches) != n:
                raise ValueError('batch coverage differs from scoring')
            seconds = sum(b['seconds_including_input_and_d2h'] for b in batches)
            timings[setting] = dict(seconds=seconds, predictions_per_second=n/seconds,
                peak_allocated_gib=max(b['peak_allocated_bytes'] for b in batches)/2**30,
                peak_reserved_gib=max(b['peak_reserved_bytes'] for b in batches)/2**30)
        counters = hardware(Path(str(run)+'_nsight.sqlite'), manifest['batches'])
        models[model] = dict(run=str(run), scores=scores, timing=timings, hardware=counters)
    if set(models) != {'pair', 'pair_free'}:
        raise ValueError('requires exactly pair and pair_free runs')
    paired = {}
    for setting in settings:
        paired[setting] = {}
        for metric in ['tm_fixed_reference', 'ca_lddt']:
            a = means_by_target(models['pair_free']['scores']['records'], setting, metric)
            b = means_by_target(models['pair']['scores']['records'], setting, metric)
            paired[setting][metric] = paired_comparison(a, b)
    step_gain = {}
    for model, data in models.items():
        rows = data['scores']['records']
        step_gain[model] = paired_comparison(means_by_target(rows, 'steps25_cfg2', 'tm_fixed_reference'),
                                             means_by_target(rows, 'steps50_cfg2', 'tm_fixed_reference'))
    result = dict(status='complete', models={k: {**v, 'scores': v['scores']['summaries']} for k, v in models.items()},
                  pair_minus_pair_free=paired, steps50_minus_steps25_cfg2=step_gain,
                  uncertainty='95% paired target-bootstrap CI after averaging three samples per target; no homology clusters available; exploratory development-set comparisons.')
    lines = ['# Frozen-head comparison', '',
             'All targets and samples are retained; no best-of-three selection. Fixed residue correspondence TM-score (USalign -TMscore 1) and CA lDDT. Timings cover cached embeddings to coordinates, including transfers; ESMC extraction is excluded.', '',
             'These are separately trained legacy checkpoints. Their difference does not isolate the causal effect of adding a pair track.', '',
             '| Model | Steps / guidance | Mean TM | CA lDDT | Predictions/s | Allocated / reserved GiB |',
             '|---|---|---:|---:|---:|---:|']
    for model, data in models.items():
        for setting in settings:
            s, t = data['scores']['summaries'][setting], data['timing'][setting]
            lines.append(f"| {model} | {setting} | {s['mean_tm_fixed_reference']:.5f} | {s['mean_ca_lddt']:.5f} | {t['predictions_per_second']:.2f} | {t['peak_allocated_gib']:.1f} / {t['peak_reserved_gib']:.1f} |")
    lines += ['', '## Paired results', '', result['uncertainty'], '',
              '| Setting | Pair minus pair-free TM | 95% CI |', '|---|---:|---|']
    for setting, metrics in paired.items():
        d = metrics['tm_fixed_reference']
        lines.append(f"| {setting} | {d['theirs_minus_ours']:.5f} | [{d['ci95'][0]:.5f}, {d['ci95'][1]:.5f}] |")
    for model, d in step_gain.items():
        lines += ['', f"{model}: going from 25 to 50 steps at guidance 2 changes mean TM by {d['theirs_minus_ours']:.5f} (95% CI [{d['ci95'][0]:.5f}, {d['ci95'][1]:.5f}])."]
    lines += ['', '## Hardware counters', '',
              'SM activity includes waiting warps and is not percent of peak FLOPs. Instruction issue and tensor activity are reported separately. Strict FP32 is the correctness reference; these results do not establish efficient BF16 inference.', '',
              '| Model | Scope | SM active % | SM issue % | Tensor active % |', '|---|---|---:|---:|---:|']
    for model, data in models.items():
        for scope in ['whole_capture_mean_percent', 'collection_mean_percent']:
            h = data['hardware'][scope]
            lines.append(f"| {model} | {scope} | {h[COUNTERS[0]]:.1f} | {h[COUNTERS[1]]:.1f} | {h[COUNTERS[2]]:.1f} |")
    lines += ['', '## Interpretation and next work', '',
              'Choose sampling settings using this development set, then freeze them for a separate test set. More sampling steps are useful only if their accuracy gain justifies measured cost. Compare checkpoint quality separately from architectural causality: a controlled training ablation remains required.', '',
              'The next efficiency experiment should preserve this FP32 reference while testing which operations need higher precision. Missing original residue maps and sequence-homology controls remain unresolved dataset limitations. Do not compare these fixed-correspondence scores directly with the earlier report without auditing its alignment protocol.', '']
    atomic_text(output.with_suffix('.json'), json.dumps(result, indent=2, allow_nan=False)+'\n')
    atomic_text(output.with_suffix('.md'), '\n'.join(lines))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, nargs=2, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = analyze(a.runs, a.output)
    print(json.dumps({'status': result['status'], 'report': str(a.output.with_suffix('.md'))}))


if __name__ == '__main__':
    main()
