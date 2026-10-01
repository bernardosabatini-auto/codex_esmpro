"""Normalize measured SM-issue activity by complete own-job allocation time."""
import argparse,json
from pathlib import Path


def seconds(text):
    days=0
    if '-' in text:
        day,text=text.split('-');days=int(day)
    parts=[int(x) for x in text.split(':')]
    if len(parts)!=3:raise ValueError('expected Slurm HH:MM:SS elapsed time')
    return days*86400+parts[0]*3600+parts[1]*60+parts[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--jobs',nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    registry={j['id']:j for j in json.loads((root/'runs/jobs.json').read_text())['jobs']};states=json.loads((root/'runs/watch/state.json').read_text())['jobs'];rows=[]
    for ident in a.jobs:
        job=registry[ident]
        if job['gpus']!=1 or job.get('tasks'):raise ValueError('single-GPU own jobs only')
        state=states[ident]['tasks'][ident]
        if state['state']!='COMPLETED' or state['exit_code']!='0:0':raise ValueError('completed successful own job required')
        prefix=job['completion_action'].removeprefix('summarize_');report=root/f'reports/{prefix}_{ident}.json';result=json.loads(report.read_text());h=result.get('hardware',{});elapsed=seconds(state['elapsed'])
        r=dict(job=ident,purpose=job['purpose'],allocated_seconds=elapsed,arm=result.get('arm'),peak_reserved_gib=result.get('max_reserved_gib',result.get('peak_reserved_gib')))
        if 'whole_capture_mean_percent' in h:
            duration=h['capture_seconds']
            if duration>elapsed+2:raise ValueError('capture exceeds Slurm allocation')
            issue=h['whole_capture_mean_percent']['SM Issue [Throughput %]']
            r.update(capture_seconds=duration,capture_sm_issue_percent=issue,work_sm_issue_percent=h['collection_mean_percent']['SM Issue [Throughput %]'],allocation_normalized_measured_sm_issue_percent=issue*duration/elapsed)
        else:r['counter_error']=h.get('error','No validated counter report')
        rows.append(r)
    d=dict(status='complete',rows=rows,scope='Only registered single-GPU jobs. Allocation-normalized measured SM issue is capture-average SM issue times capture duration divided by total Slurm elapsed time. Unmeasured time contributes zero, so startup/export overhead is included conservatively. This is an instruction-issue indicator, not measured peak-FLOP efficiency.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# GPU allocation accounting','',d['scope'],'','| Job | Arm | Allocated minutes | Capture SM issue % | Work SM issue % | Allocation-normalized measured SM issue % | Peak reserved GiB |','|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        fmt=lambda key:f"{r[key]:.2f}" if r.get(key) is not None else 'unavailable'
        lines.append(f"| {r['job']} | {r['arm'] or 'data/profile'} | {r['allocated_seconds']/60:.2f} | {fmt('capture_sm_issue_percent')} | {fmt('work_sm_issue_percent')} | {fmt('allocation_normalized_measured_sm_issue_percent')} | {fmt('peak_reserved_gib')} |")
    for r in rows:
        if 'counter_error' in r:lines+=['',f"Job {r['job']}: {r['counter_error']}. No utilization estimate is assigned."]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
