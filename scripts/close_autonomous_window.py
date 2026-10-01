"""Cancel only this project's unfinished requests from one expired work window."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess

from watch_jobs import job_ids, scheduler_states, TERMINAL, write_json


def window_ids(registry, window):
    started=datetime.fromisoformat(window['started'].replace('Z','+00:00'))
    deadline=datetime.fromisoformat(window['deadline'].replace('Z','+00:00'))
    selected=[]
    for job in registry['jobs']:
        submitted=datetime.fromisoformat(job['submitted'].replace('Z','+00:00')) if job.get('submitted') else None
        if submitted and started<=submitted<=deadline and job.get('state') not in TERMINAL:
            selected.extend(job_ids(job))
    if len(selected)!=len(set(selected)):raise ValueError('duplicate ownership')
    return selected


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--window',type=Path,required=True)
    args=parser.parse_args();root=args.root.resolve();now=datetime.now(timezone.utc)
    with (root/'runs/submit.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        window=json.loads(args.window.read_text());deadline=datetime.fromisoformat(window['deadline'].replace('Z','+00:00'))
        if now<deadline:raise ValueError('refusing to close an unexpired work window')
        if window.get('status')=='closed':return
        if window.get('status')!='active':raise ValueError('unexpected work-window status')
        ids=window_ids(json.loads((root/'runs/jobs.json').read_text()),window)
        states=scheduler_states(ids) if ids else {}
        unfinished=[ident for ident in ids if states.get(ident,{}).get('state') not in TERMINAL]
        # Every ID has been read from this project's registry and validated.
        # Missing accounting is not proof of completion; exact-ID cancellation
        # is safe even if a registered job just left the live queue.
        if unfinished:subprocess.run(['scancel',*unfinished],check=True,timeout=30)
        window.update(status='closed',closed_at=now.isoformat(),deadline_cancel_requested=unfinished)
        write_json(args.window,window)
        print(json.dumps(dict(closed_at=now.isoformat(),cancel_requested=unfinished,registered_ids=ids)),flush=True)


if __name__=='__main__':main()
