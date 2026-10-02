"""Advance only the fixed two-endpoint replay experiment, at most one job/tick."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
from watch_jobs import TERMINAL, write_json, stamp
from prepare_overfit import sha

UNIT = 'esm-proae-replay-followups.timer'
PYTHON = '/n/home08/bsabatini/.conda/envs/proteinae/bin/python'


def existing_job(root, jobs, script, step, parents, seed=None):
    found = [j for j in jobs if j.get('script') == script]
    if len(found) > 1: raise ValueError('duplicate fixed follow-up')
    if not found: return None
    job = found[0]
    config = json.loads((Path(job['code_snapshot'])/'entry_configs/0.json').read_text())
    if seed is None:
        expected = {f'seed{s}_{arm}':str((root/f'runs/overfit_{jid}/ema_{step}.ckpt').resolve()) for arm, ids in parents.items() if arm=='replay' for s,jid in zip((2026100171,2026100181),ids)}
        actual = {h['name']:h['checkpoint'] for h in config['heads'] if h['name'] != 'original'}
        if config['training_checkpoint_step'] != step or actual != expected: raise ValueError('existing native job has different lineage')
    else:
        jid = parents['replay'][(2026100171,2026100181).index(seed)]
        if config['checkpoint'] != str((root/f'runs/overfit_{jid}/ema_{step}.ckpt').resolve()): raise ValueError('existing ensemble has different lineage')
    return job


def nodes(root, plan, jobs, watch):
    """Readiness uses registered own jobs and exact checkpoint-analysis evidence."""
    parents = plan['parents']; byid = {j['id']:j for j in jobs}
    if set(parents) != {'full','replay'} or any(len(ids) != 2 for ids in parents.values()) or len({i for ids in parents.values() for i in ids}) != 4 or plan['steps'] != [500,2000]:
        raise ValueError('invalid fixed graph')
    ids = parents['full']+parents['replay']
    if any(not i.isdigit() or i not in byid or byid[i].get('completion_action') != 'summarize_overfit' for i in ids): raise ValueError('unregistered training parents')
    def state(jid): return watch.get('jobs',{}).get(jid,{}).get('tasks',{}).get(jid,{}).get('state')
    result = []
    for step in plan['steps']:
        script = f'slurm/replay_native_{step}_h200.sbatch'
        job = existing_job(root, jobs, script, step, parents)
        node = dict(kind='native', step=step, script=script, config=f'runs/replay_native_{step}_config.json', status='waiting')
        if job: node.update(status='submitted', child=job['id'])
        else:
            evidence = watch.get('overfit_checkpoints',{}).get(f'replay_{step}',{})
            if evidence.get('handled'):
                if evidence['jobs'] != ids: raise ValueError('checkpoint evidence belongs to other jobs')
                report=json.loads((root/f'reports/functional_replay_comparison_{step}.json').read_text())
                if report.get('status')!='complete' or report['step']!=step or not report['matched'] or report['training_targets']!=427:raise ValueError('wrong replay capacity report')
                node['status'] = 'eligible' if report['replicated_capacity_retained'] else 'capacity_failed'
            elif any(state(i) in TERMINAL-{'COMPLETED'} for i in parents['replay']): node['status'] = 'failed_predecessor'
        result.append(node)
        for seed in (2026100171,2026100181):
            script = f'slurm/replay_ensemble_{step}_{seed}_rtx.sbatch'
            ensemble = existing_job(root, jobs, script, step, parents, seed)
            child = dict(kind='ensemble', step=step, seed=seed, script=script, config=f'runs/replay_ensemble_{step}_{seed}.json', status='waiting')
            if ensemble: child.update(status='submitted', child=ensemble['id'])
            elif node['status'] in ('failed_predecessor','capacity_failed'): child['status'] = node['status']
            elif job:
                if state(job['id']) in TERMINAL-{'COMPLETED'}: child['status'] = 'failed_predecessor'
                elif state(job['id']) == 'COMPLETED':
                    report = root/f"reports/replay_native_{job['id']}.json"
                    if report.exists():
                        d = json.loads(report.read_text())
                        if d['status'] != 'complete': child['status'] = 'failed_predecessor'
                        else:
                            if d['step'] != step or d.get('training_targets')!=427 or d.get('replay_targets')!=390: raise ValueError('wrong native result')
                            child.update(status='eligible' if d['summaries'][f'seed{seed}_replay_cfg1']['quality_passed'] else 'quality_failed', parent=job['id'])
            result.append(child)
    return result


def tick(root, dry_run=False):
    root = Path(root).resolve()
    plan = json.loads((root/'runs/replay_followups.json').read_text())
    policy = json.loads((root/'runs/execution_policy.json').read_text())
    if plan['status'] != 'active' or policy['status'] != 'active': return dict(status='inactive')
    with (root/'runs/replay_followups.lock').open('w') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return dict(status='locked')
        for path, digest in plan['code_sha256'].items():
            if sha(root/path) != digest: raise ValueError('fixed follow-up code changed: '+path)
        jobs = json.loads((root/'runs/jobs.json').read_text())['jobs']
        watch = json.loads((root/'runs/watch/state.json').read_text())
        result = dict(checked_at=stamp(), nodes=nodes(root,plan,jobs,watch), submitted=None)
        deadline = datetime.datetime.fromisoformat(policy['deadline_utc'])
        expired = datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=17) > deadline
        for node in result['nodes']:
            if expired and node['status'] in ('waiting','eligible'): node['status'] = 'deadline_closed'
            if node['status'] != 'eligible' or dry_run or result['submitted']: continue
            env = dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONPATH=str(root/'src'))
            if node['kind'] == 'native':
                prepare = [PYTHON,'scripts/prepare_replay_native.py','--full',*[f'runs/overfit_{i}' for i in plan['parents']['full']],'--candidate',*[f'runs/overfit_{i}' for i in plan['parents']['replay']],'--step',str(node['step']),'--output',node['config']]
                action = 'summarize_replay_native'
            else:
                prepare = [PYTHON,'scripts/prepare_replay_ensemble.py','--screen',f"runs/replay_native_{node['parent']}",'--head',f"seed{node['seed']}_replay",'--output',node['config']]
                action = 'summarize_ensemble'
            try:
                subprocess.run(prepare,cwd=root,env=env,text=True,capture_output=True,timeout=90,check=True)
                command = [PYTHON,'scripts/submit_registered.py','--script',node['script'],'--purpose',f"Fixed local replay {node['kind']} follow-up at{node['step']}, seed{node.get('seed','both')}",'--minutes','15','--action',action]
                completed = subprocess.run(command,cwd=root,env=env,text=True,capture_output=True,check=True)
                result['submitted'] = json.loads(completed.stdout)['submitted']; node.update(status='submitted',child=result['submitted'])
            except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
                node.update(status='retry',error=str(error.stderr or error)[-2000:]); break
        resolved = all(n['status'] in ('submitted','quality_failed','capacity_failed','failed_predecessor','deadline_closed') for n in result['nodes'])
        result['status'] = 'resolved' if resolved else 'active'
        if not dry_run:
            write_json(root/'runs/replay_followups_state.json',result)
            if resolved: subprocess.run(['systemctl','--user','stop',UNIT],timeout=10,check=True)
        return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
    print(json.dumps(tick(Path(__file__).resolve().parents[1],a.dry_run)))
