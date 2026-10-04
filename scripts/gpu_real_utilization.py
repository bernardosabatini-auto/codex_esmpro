"""Kempner's exact four-counter composite; never substitute NVML or VRAM use."""
import argparse,json,math
from pathlib import Path


FIELDS=('gr_engine_active','sm_active','tensor_active','dram_active')
WEIGHTS=(.10,.35,.35,.20)


def parse_dcgm(text,gpu_index):
    header=False;rows=[];invalid=0
    for line in text.splitlines():
        parts=line.split()
        if parts and parts[0]=='#Entity':
            if parts[1:]!=['GRACT','SMACT','TENSO','DRAMA']:raise ValueError('Unexpected DCGM field order')
            header=True
        if not parts or parts[0]!='GPU':continue
        if not header or len(parts)!=6 or parts[1]!=str(gpu_index):raise ValueError('Unbound GPU or counter columns')
        try:values=[float(v) for v in parts[2:]]
        except ValueError:
            invalid+=1;continue
        if any(not math.isfinite(v) or not 0<=v<=1 for v in values):invalid+=1;continue
        rows.append(values)
    if not rows:return dict(status='unavailable',valid_samples=0,invalid_samples=invalid,reason='No finite complete four-counter rows')
    means=[sum(r[i] for r in rows)/len(rows) for i in range(4)]
    result=dict(status='complete',valid_samples=len(rows),invalid_samples=invalid,complete_fraction=len(rows)/(len(rows)+invalid),means=dict(zip(FIELDS,means)),real_utilization_percent=100*min(1,max(0,sum(w*v for w,v in zip(WEIGHTS,means)))))
    if len(rows)<10 or result['complete_fraction']<.95:
        result.update(status='insufficient_coverage');result.pop('real_utilization_percent')
    return result


def analyze(root,jid):
    jobs={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if jid not in jobs or jobs[jid]['gpus']!=1 or jobs[jid].get('tasks'):raise ValueError('One registered own GPU job required')
    job=jobs[jid];prefix=job['completion_action'].removeprefix('summarize_');run=root/'runs'/f'{prefix}_{jid}'
    meta=json.loads((run/'device_metadata.json').read_text());path=run/'dcgm.txt'
    verified=run/'dcgm_verified_metadata.json'
    if verified.exists():
        sidecar=json.loads(verified.read_text())
        if sidecar.get('uuid_verified') is not True or sidecar['uuid']!=meta['uuid'] or sidecar['job']!=jid:
            raise ValueError('Unbound replacement counter capture')
        path=run/'dcgm_verified.txt';meta=dict(meta,dcgm_gpu_index=sidecar['dcgm_gpu_index'],dcgm_fields=sidecar['dcgm_fields'],dcgm_uuid_verified=True)
    if not path.exists() or meta.get('dcgm_fields')!=[1001,1002,1004,1005] or meta.get('dcgm_uuid_verified') is not True:
        result=dict(status='unavailable',reason='Four-counter capture with verified assigned UUID required')
    else:result=parse_dcgm(path.read_text(),meta['dcgm_gpu_index'])
    return dict(result,job=jid,uuid=meta['uuid'],scope='Mean over available one-second four-counter samples on this assigned GPU. Excludes time before recorder startup. Not the dashboard24-hour/hourly-allocation statistic. No other jobs or GPUs queried.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--output',type=Path);a=p.parse_args();d=analyze(Path(__file__).resolve().parents[1],a.job)
    if a.output:a.output.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d,indent=2))


if __name__=='__main__':main()
