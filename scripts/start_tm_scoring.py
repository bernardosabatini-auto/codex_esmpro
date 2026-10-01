"""Start one bounded, registered CPU comparison of two completed own training jobs."""
import argparse,fcntl,json,subprocess
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('cached','reflow'),required=True);p.add_argument('--jobs',nargs=2,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    jobs=json.loads((root/'runs/jobs.json').read_text())['jobs'];prefix='distillation' if a.kind=='cached' else 'reflow';expected={'cached_reference','cached_aligned_empirical'} if a.kind=='cached' else {'reflow_paired','reflow_independent'};arms=set();runs=[]
    for ident in a.jobs:
        found=[j for j in jobs if j['id']==ident]
        if len(found)!=1 or found[0]['completion_action']!='summarize_'+prefix:raise ValueError('unregistered training source')
        run=root/f'runs/{prefix}_{ident}';m=json.loads((run/'manifest.json').read_text())
        if m['status']!='complete' or m['updates']!=2000:raise ValueError('training evaluation incomplete')
        arms.add(m['config']['arm']);runs.append(str(run))
    if arms!=expected:raise ValueError('incorrect comparison arms')
    unit=f'esm-proae-tm-{a.kind}-'+ '-'.join(a.jobs)+'.service';output=root/'runs'/('tm_'+a.kind+'_'+'_'.join(a.jobs))
    registry_path=root/'runs/local_jobs.json';python='/n/home08/bsabatini/.conda/envs/proteinae/bin/python'
    with (root/'runs/local_jobs.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);registry=json.loads(registry_path.read_text())
        if any(j['unit']==unit for j in registry['jobs']):print(unit);return
        subprocess.run(['git','diff','--quiet','HEAD','--','src','scripts'],cwd=root,check=True)
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();snapshot=root/'runs/code_snapshots'/(commit[:12]+'_tm_'+a.kind+'_'+'_'.join(a.jobs))
        if not snapshot.exists():
            snapshot.mkdir();archive=snapshot/'source.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),commit],cwd=root,check=True);subprocess.run(['tar','-xf',str(archive),'-C',str(snapshot)],check=True);archive.unlink();(snapshot/'runs').symlink_to(root/'runs',target_is_directory=True)
        record=dict(unit=unit,status_path=str(output.relative_to(root)/'score.json'),action='summarize_tm_scores',report=output.name,source_jobs=a.jobs,code_commit=commit,code_snapshot=str(snapshot));registry['jobs'].append(record)
        def save():
            temp=registry_path.with_suffix('.tmp');temp.write_text(json.dumps(registry,indent=2)+'\n');temp.replace(registry_path)
        save()
        command=['systemd-run','--user','--unit='+unit,'--property=WorkingDirectory='+str(snapshot),'--property=CPUQuota=200%','--property=MemoryMax=4G','--property=RuntimeMaxSec=1800']
        command+=['--setenv='+x for x in ('CUDA_VISIBLE_DEVICES=','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','PYTHONPATH=src','PYTHONDONTWRITEBYTECODE=1','LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib')]
        command += [python,'scripts/score_distillation_tm.py' if a.kind=='cached' else 'scripts/score_reflow_tm.py','--runs',*runs,'--usalign',str(root/'runs/tools/USalign/USalign'),'--references',str(root/'runs/tuning_sources'),'--output',str(output)]
        if a.kind=='cached':command+=['--control','cached_reference']
        try:subprocess.run(command,check=True,capture_output=True,text=True,timeout=20)
        except BaseException:registry['jobs'].remove(record);save();raise
        print(unit)


if __name__=='__main__':main()
