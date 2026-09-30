"""Bounded one-CPU fallback when the CPU Slurm association is disabled.

Run as a project-specific systemd user unit with CPU/memory/time limits. Always
attempt a CPU report when the child finishes; no GPU access or scheduler calls.
"""
import json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[1]
run=root/'runs/holdout_local_20260930'
with (root/'runs/holdout_local_20260930.out').open('a') as log:
 result=subprocess.run([sys.executable,'-u',str(root/'scripts/prepare_holdout.py'),
    '--source','/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae','--output',str(run),'--threads','1'],
    cwd=root,stdout=log,stderr=subprocess.STDOUT)
 analysis=subprocess.run([sys.executable,str(root/'scripts/summarize_holdout.py'),'--runs',str(run),
    '--output',str(root/'reports/holdout_local_20260930')],cwd=root,stdout=log,stderr=subprocess.STDOUT)
 event=dict(time=datetime.now(timezone.utc).isoformat(),key='holdout_local_20260930:finished',
    message=f'CPU holdout preparation exit={result.returncode}; analysis exit={analysis.returncode}; reports/holdout_local_20260930.md')
 with (root/'runs/watch/events.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
sys.exit(result.returncode or analysis.returncode)
