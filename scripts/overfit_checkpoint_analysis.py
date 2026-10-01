"""Bounded CPU comparisons for explicitly registered overfit checkpoints."""
import json
import os
import re
import subprocess
import time


def tick(root,state,registry,config,run=subprocess.run):
    plan=root/'runs/overfit_checkpoint_analyses.json'
    if not plan.exists():return []
    jobs={j['id']:j for j in registry['jobs']}
    specs=json.loads(plan.read_text())['comparisons']
    # Validate the whole plan before reading any run paths or executing anything.
    for spec in specs:
        ids=spec['jobs'];kind=spec['kind']
        if kind not in ('empirical','balanced') or len(ids)!=(3 if kind=='empirical' else 5) or len(set(ids))!=len(ids):raise ValueError('invalid checkpoint comparison')
        if any(not re.fullmatch(r'\d+',i) or i not in jobs or jobs[i].get('completion_action')!='summarize_overfit' for i in ids):raise ValueError('checkpoint comparison must use registered overfit jobs')
        if spec['steps']!=[500,2000]:raise ValueError('unrecognized checkpoint schedule')
    entries=state.setdefault('overfit_checkpoints',{})
    for spec in specs:
        for step in spec['steps']:
            key=f"{spec['kind']}_{step}";entry=entries.setdefault(key,{})
            if entry.get('handled') and entry.get('jobs')!=spec['jobs']:raise ValueError('completed checkpoint plan changed')
            if entry.get('handled') or time.time()<entry.get('retry_after',0):continue
            paths=[root/'runs'/f'overfit_{i}' for i in spec['jobs']]
            if not all((p/'manifest.json').exists() for p in paths):continue
            manifests=[json.loads((p/'manifest.json').read_text()) for p in paths]
            ready=True
            for m in manifests:
                if m['status'] not in ('running','complete') or m['updates']<step:ready=False;break
                for checkpoint in (0,step):
                    for guidance in (1,2):
                        rows=[r for r in m['scores'] if r['step']==checkpoint and r['guidance']==guidance]
                        if len(rows)!=32 or len({r['target_id'] for r in rows})!=32:ready=False
            if not ready:continue
            prefix='overfit' if spec['kind']=='empirical' else 'overfit_balanced'
            report=root/'reports'/f'{prefix}_comparison_{step}'
            frequency=root/'reports'/f'{prefix}_state_frequency_{step}'
            script='compare_overfit.py' if spec['kind']=='empirical' else 'compare_overfit_balanced.py'
            env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONPATH=str(root/'src'))
            entry.update(jobs=spec['jobs'],step=step)
            try:
                with (root/'runs/watch'/f'checkpoint_{key}.log').open('a') as log:
                    for name,output in ((script,report),('analyze_overfit_states.py',frequency)):
                        command=[config['python'],str(root/'scripts'/name),'--runs',*[str(p) for p in paths],'--step',str(step),'--output',str(output)]
                        run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=45,check=True)
                entry.update(handled=True,report=str(report.with_suffix('.md')),frequency_report=str(frequency.with_suffix('.md')),completed_at=time.time())
                return [(f'overfit_checkpoint:{key}:complete',f'ESM project {key} checkpoint comparisons ready at {report.with_suffix(".md")}.')]
            except Exception as error:
                entry.update(error=str(error),retry_after=time.time()+120)
                return [(f'overfit_checkpoint:{key}:failed',f'ESM project {key} checkpoint analysis failed; see runs/watch/checkpoint_{key}.log. Retry scheduled.')]
    return []
