"""Reject unregistered IDs before issuing any manual scheduler query."""
import argparse,json
from pathlib import Path
from watch_jobs import job_ids,scheduler_states


def resolve(jobs, *, ids=None, scripts=None):
    if bool(ids)==bool(scripts):raise ValueError('provide registered IDs or exact registered script paths')
    selected=[]
    if scripts:
        for script in scripts:
            matches=[j for j in jobs if j.get('script')==script]
            if len(matches)!=1:raise ValueError('script must identify exactly one registered job: '+script)
            selected.extend(job_ids(matches[0]))
    else:
        parents={j['id']:j for j in jobs};tasks={i for j in jobs for i in job_ids(j)}
        for ident in ids:
            if ident in parents:selected.extend(job_ids(parents[ident]))
            elif ident in tasks:selected.append(ident)
            else:raise ValueError('refusing unregistered job ID: '+ident)
    return list(dict.fromkeys(selected))


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--ids',nargs='+');g.add_argument('--scripts',nargs='+');a=p.parse_args()
    root=Path(__file__).resolve().parents[1];jobs=json.loads((root/'runs/jobs.json').read_text())['jobs']
    ids=resolve(jobs,ids=a.ids,scripts=a.scripts)
    print(json.dumps(scheduler_states(ids),indent=2))


if __name__=='__main__':main()
