"""Start a bounded CPU scorer for one explicitly registered, completed ensemble."""
import argparse,fcntl,json,subprocess
from pathlib import Path


def start(root, job_id):
    root=Path(root).resolve();jobs=json.loads((root/'runs/jobs.json').read_text())['jobs'];matches=[j for j in jobs if j['id']==job_id]
    if len(matches)!=1:raise ValueError('expected one explicitly registered own job')
    job=matches[0];prefix={'summarize_ensemble':'ensemble','summarize_teacher_ensemble':'teacher_ensemble','summarize_retry_ensemble':'retry_ensemble'}.get(job.get('completion_action'))
    if prefix is None:raise ValueError('job has no ensemble scoring action')
    run=root/'runs'/f'{prefix}_{job_id}';manifest=json.loads((run/'manifest.json').read_text())
    if manifest['status']!='complete':raise ValueError('ensemble predictions incomplete')
    unit=f'esm-proae-state-scores-{job_id}.service';path=root/'runs/local_jobs.json';python='/n/home08/bsabatini/.conda/envs/proteinae/bin/python'
    with (root/'runs/local_jobs.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);registry=json.loads(path.read_text())
        if any(j['unit']==unit for j in registry['jobs']):return unit
        record=dict(unit=unit,status_path=f'runs/state_scores_{job_id}/score.json',action='summarize_state_scores',report=f'state_scores_{job_id}',source_job=job_id,code_commit=job['code_commit'])
        registry['jobs'].append(record);temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(registry,indent=2)+'\n');temporary.replace(path)
        snapshot=Path(job['code_snapshot']);command=['systemd-run','--user','--unit='+unit,'--property=WorkingDirectory='+str(snapshot),'--property=CPUQuota=100%','--property=MemoryMax=4G','--property=RuntimeMaxSec=3600']
        command+=['--setenv='+x for x in ('CUDA_VISIBLE_DEVICES=','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','PYTHONPATH=src','LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib')]
        command+=[python,'scripts/score_ensemble_states.py','--run',str(run),'--assets',str(root/'runs/ensemble_sources/bioemu_benchmarks_pinned'),'--protocol','configs/ensemble_scoring_protocol.json','--output',str(root/f'runs/state_scores_{job_id}/score')]
        try:subprocess.run(command,check=True,timeout=20,capture_output=True,text=True)
        except BaseException:
            registry['jobs'].remove(record);temporary.write_text(json.dumps(registry,indent=2)+'\n');temporary.replace(path);raise
    return unit


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);a=p.parse_args();print(start(Path(__file__).resolve().parents[1],a.job))
