"""Verify that two training arms differ only in their declared label/noise arm."""
import argparse,hashlib,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs=2,type=Path,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifests=[];sources={}
    for run in a.runs:
        path=run/'manifest.json';raw=path.read_bytes();m=json.loads(raw);sources[str(path.resolve())]=hashlib.sha256(raw).hexdigest()
        if m['status'] not in ('running','complete') or m['updates']<a.step:raise ValueError('checkpoint unavailable')
        manifests.append(m)
    left,right=manifests;arms={m['config']['arm'] for m in manifests}
    if arms not in ({'cached_reference','cached_aligned_empirical'},{'reflow_paired','reflow_independent'}):raise ValueError('unexpected arm pair')
    configs=[{k:v for k,v in m['config'].items() if k!='arm'} for m in manifests]
    if configs[0]!=configs[1]:raise ValueError('training configs differ beyond declared arm')
    if left['checkpoint']['sha256']!=right['checkpoint']['sha256']:raise ValueError('initial checkpoints differ')
    keys=('step','length','batch','learning_rate','ids_sha256')
    logs=[[{k:r[k] for k in keys} for r in m['training'] if r['step']<=a.step] for m in manifests]
    if logs[0]!=logs[1] or not logs[0] or logs[0][-1]['step']!=a.step:raise ValueError('target order, batch or learning-rate schedule differs')
    initial=[[{k:v for k,v in r.items() if k in ('step','target_id','sample','sampling_steps')} for r in m['scores'] if r['step']==0] for m in manifests]
    if initial[0]!=initial[1] or len(initial[0])!=192:raise ValueError('initial evaluation identity mismatch')
    result=dict(status='complete',arms=sorted(arms),step=a.step,source_manifest_sha256=sources,identical_config_except_arm=True,identical_initial_checkpoint=True,identical_logged_target_batches_and_learning_rates=True,logged_updates=len(logs[0]))
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
