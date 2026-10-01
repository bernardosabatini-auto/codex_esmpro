"""Submit only the predeclared final-checkpoint ensemble follow-ups."""
import argparse,fcntl,json,os,subprocess
from pathlib import Path
from watch_jobs import TERMINAL,write_json,stamp
from reflow_quality import native_screen


def tick(root, *, dry_run=False):
    root=Path(root).resolve();plan=json.loads((root/'runs/checkpoint_followups.json').read_text());policy=json.loads((root/'runs/execution_policy.json').read_text())
    if plan['status']!='active' or policy['status']!='active':return
    python='/n/home08/bsabatini/.conda/envs/proteinae/bin/python'
    with (root/'runs/checkpoint_followups.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        jobs=json.loads((root/'runs/jobs.json').read_text())['jobs'];byid={j['id']:j for j in jobs};watch=json.loads((root/'runs/watch/state.json').read_text())['jobs'];result=dict(checked_at=stamp(),nodes=[],submitted=None)
        for node in plan['nodes']:
            parent=node['parent'];source=byid.get(parent)
            if source is None or source.get('completion_action') not in ('summarize_distillation','summarize_reflow'):raise ValueError('unregistered training predecessor')
            reflow=source['completion_action']=='summarize_reflow'
            prefix='reflow' if reflow else 'distillation'
            if reflow and node.get('sampling_steps') not in (5,10):raise ValueError('missing predeclared sampler steps')
            checkpoint=str(root/f'runs/{prefix}_{parent}/ema_2000.ckpt');existing=[]
            for job in jobs:
                if job.get('script')!=node['script']:continue
                config=json.loads((Path(job['code_snapshot'])/'entry_configs/0.json').read_text())
                if config.get('checkpoint')==checkpoint:existing.append(job['id'])
            if existing:
                if len(existing)!=1:raise ValueError('duplicate checkpoint follow-up')
                result['nodes'].append(dict(parent=parent,child=existing[0],status='submitted'));continue
            terminal=watch.get(parent,{}).get('tasks',{}).get(parent,{})
            state=terminal.get('state')
            if state!='COMPLETED' or terminal.get('exit_code')!='0:0':
                result['nodes'].append(dict(parent=parent,status='failed_predecessor' if state in TERMINAL else 'waiting'));continue
            manifest=json.loads((root/f'runs/{prefix}_{parent}/manifest.json').read_text())
            if manifest['status']!='complete' or manifest['config']['arm']!=node['arm'] or manifest['updates']!=2000:raise ValueError('predecessor result mismatch')
            if reflow:
                screen=native_screen(manifest,2000,node['sampling_steps'])
                if not screen['passed']:
                    result['nodes'].append(dict(parent=parent,sampling_steps=node['sampling_steps'],status='screen_failed',native_quality_screen=screen));continue
            result['nodes'].append(dict(parent=parent,status='eligible'))
            if dry_run or result['submitted'] is not None:continue
            env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONPATH=str(root/'src'))
            prepare=[python,'scripts/prepare_reflow_ensemble.py' if reflow else 'scripts/prepare_trained_ensemble.py','--run',f'runs/{prefix}_{parent}','--step','2000','--output',node['config']]
            if reflow:prepare+=['--sampling-steps',str(node['sampling_steps'])]
            try:
                subprocess.run(prepare,cwd=root,env=env,capture_output=True,text=True,check=True,timeout=90)
                env.pop('CUDA_VISIBLE_DEVICES',None)
                command=[python,'scripts/submit_registered.py','--script',node['script'],'--purpose',f"Predeclared final ensemble follow-up of own training{parent}, arm{node['arm']},2000updates",'--minutes','30','--action','summarize_ensemble']
                completed=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,check=True);result['submitted']=json.loads(completed.stdout)['submitted'];result['nodes'][-1].update(status='submitted',child=result['submitted'])
            except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
                result['nodes'][-1].update(status='retry',error=str(error.stderr or error)[-2000:]);break
            # One submission per tick keeps GPU-capacity decisions and heartbeat checks fresh.
        if dry_run:return result
        result['status']='all_submitted' if all(n['status']=='submitted' for n in result['nodes']) else ('all_resolved' if all(n['status'] in ('submitted','screen_failed') for n in result['nodes']) else 'active')
        write_json(root/'runs/checkpoint_followups_state.json',result)
        if result['status'] in ('all_submitted','all_resolved'):subprocess.run(['systemctl','--user','stop','esm-proae-reboot-checkpoint-followups.timer'],check=True,timeout=10)

        return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');a=p.parse_args();result=tick(Path(__file__).resolve().parents[1],dry_run=a.dry_run)
    if a.dry_run:print(json.dumps(result))
