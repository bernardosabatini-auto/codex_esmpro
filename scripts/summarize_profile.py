"""Join Nsight hardware counters to completed profile NVTX intervals.

Uses elapsed-time sampling, not kernel-only averages. Counter names and units
are obtained from the trace. SM activity is not model FLOP utilization.
"""
import argparse
from bisect import bisect_right
from collections import defaultdict
import json
from pathlib import Path
import sqlite3


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--sqlite', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    report = json.loads(a.profile.read_text())
    if report['status'] != 'completed_profile':
        raise ValueError('requires completed profiling run')
    # Immutable avoids filesystem read-lock traffic on this completed export.
    connection = sqlite3.connect(a.sqlite.resolve().as_uri()+'?mode=ro&immutable=1', uri=True)
    names = ['SMs Active [Throughput %]', 'SM Issue [Throughput %]',
             'Tensor Active [Throughput %]', 'DRAM Read Bandwidth [Throughput %]',
             'DRAM Write Bandwidth [Throughput %]']
    catalog = connection.execute('select typeId,metricId,metricName from TARGET_INFO_GPU_METRICS').fetchall()
    chosen = {mid: name for _, mid, name in catalog if name in names}
    types = {kind for kind, _, name in catalog if name in names}
    if set(chosen.values()) != set(names) or len(types) != 1:
        raise ValueError('missing or ambiguous GPU hardware counters')
    intervals = connection.execute("select start,end,text from NVTX_EVENTS where text like 'measure::%' order by start").fetchall()
    if not intervals or any(end is None or end <= start for start, end, _ in intervals):
        raise ValueError('invalid measurement intervals')
    if any(intervals[i][1] > intervals[i+1][0] for i in range(len(intervals)-1)):
        raise ValueError('overlapping measurement intervals')
    starts = [r[0] for r in intervals]
    totals, global_totals = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    first_sm, last_sm, sm_count = None, None, 0
    sm_id = next(k for k, v in chosen.items() if v == names[0])
    placeholders = ','.join('?' for _ in chosen)
    query = f'select timestamp,metricId,value from GPU_METRICS where typeId=? and metricId in ({placeholders})'
    for tick, metric, value in connection.execute(query, [next(iter(types)), *chosen]):
        if not 0 <= value <= 100:
            raise ValueError('unexpected percentage counter value')
        global_totals[metric][0] += value
        global_totals[metric][1] += 1
        if metric == sm_id:
            first_sm = tick if first_sm is None else min(first_sm, tick)
            last_sm = tick if last_sm is None else max(last_sm, tick)
            sm_count += 1
        i = bisect_right(starts, tick)-1
        if i >= 0 and tick < intervals[i][1]:
            totals[i, metric][0] += value
            totals[i, metric][1] += 1
    period = (last_sm-first_sm)/(sm_count-1)
    hardware = {}
    for i, (start, end, name) in enumerate(intervals):
        counts = [totals[i, mid][1] for mid in chosen]
        coverage = min(counts)*period/(end-start)
        if coverage < 0.95 or coverage > 1.05:
            raise ValueError(f'incomplete hardware counter coverage for {name}: {coverage}')
        hardware[name] = dict(mean_percent={chosen[mid]: totals[i, mid][0]/totals[i, mid][1] for mid in chosen},
                              coverage_fraction=coverage, samples=min(counts), seconds=(end-start)/1e9)
    rows = []
    for row in report['rows']:
        if row['status'] == 'ok':
            rows.append(dict(row, hardware=hardware[row['nvtx_range']]))
    selections = []
    for checkpoint, length in sorted({(r['checkpoint'], r['padded_length']) for r in rows}):
        matching = [r for r in rows if r['checkpoint'] == checkpoint and r['padded_length'] == length]
        best = max(r['proteins_per_second'] for r in matching)
        eligible = [r for r in matching if r['proteins_per_second'] >= 0.95*best
                    and r['peak_reserved_bytes'] < 0.85*report['gpu_bytes']
                    and r['hardware']['mean_percent'][names[0]] >= 50]
        if not eligible:
            raise ValueError(f'no efficient batch passes SM/memory gates: {checkpoint}, L{length}')
        selections.append(min(eligible, key=lambda r: r['batch']))
    summary = dict(status='passed', profile_job_id=report['job_id'],
                   profile=str(a.profile), trace=str(a.sqlite),
                   selection='smallest measured batch within 95% of best throughput, SM activity >=50%, reserved memory <85%',
                   caveat='SMs Active includes warps waiting on memory; it is not percent of peak BF16 FLOPs. Tensor activity is separately reported.',
                   whole_capture_mean_percent={chosen[mid]: total/count for mid, (total,count) in global_totals.items()},
                   counter_period_ns=period, selected=selections, rows=rows)
    a.output.write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps(summary['whole_capture_mean_percent'], indent=2))
    for row in selections:
        print(row['checkpoint'], row['padded_length'], row['batch'],
              round(row['proteins_per_second'],2), row['hardware']['mean_percent'], flush=True)


if __name__ == '__main__':
    main()
