"""One bounded watcher tick: inspect only registered jobs and run fixed CPU follow-ups.

Run every minute via the project systemd timer. Does not submit/cancel GPU jobs,
start agents, type into tmux, or modify the GPU job registry. Completed ensembles
start explicitly registered, bounded CPU state scorers.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

TERMINAL = {'COMPLETED', 'FAILED', 'FAILED_CONTROLS', 'CANCELLED', 'TIMEOUT',
            'OUT_OF_MEMORY', 'NODE_FAIL', 'BOOT_FAIL', 'DEADLINE', 'PREEMPTED', 'REVOKED'}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2)+'\n')
    temp.replace(path)


def job_ids(job):
    if not re.fullmatch(r'\d+', job['id']):
        raise ValueError('invalid registered job ID')
    ids = job.get('tasks', [job['id']])
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('empty or duplicate task IDs')
    if any(not re.fullmatch(re.escape(job['id']) + r'(?:_\d+)?', i) for i in ids):
        raise ValueError('task IDs must belong to their registered parent')
    return ids


def scheduler_states(ids, run=subprocess.run):
    # -X suppresses steps; filter exact requested task IDs again after parsing.
    completed = run(['sacct', '-X', '-n', '-P', '-j', ','.join(ids),
                     '--format=JobID%40,State%40,ExitCode,Elapsed,End'],
                    capture_output=True, text=True, timeout=20, check=True)
    # Use display IDs, since JobIDRaw differs for array tasks. Exact match only.
    rows = {}
    for line in completed.stdout.splitlines():
        parts = line.split('|')
        if len(parts) < 5 or parts[0] not in ids:
            continue
        name, state, code, elapsed, end = parts[:5]
        rows[name] = dict(state=state.split()[0].rstrip('+'), exit_code=code,
                          elapsed=elapsed, ended=end)
    # Live allocation state takes precedence: accounting can already say
    # COMPLETED while squeue still reports COMPLETING and holds the GPU.
    # Query only exact owned IDs, expanding arrays. A query failure propagates;
    # neither completion handling nor the submission cap may assume release.
    if ids:
        live=run(['squeue','-h','-r','-j',','.join(ids),'--format=%i|%T|%M'],
                 capture_output=True,text=True,timeout=20,check=True)
        for line in live.stdout.splitlines():
            fields=line.strip().split('|')
            if len(fields)==3 and fields[0] in ids:
                rows[fields[0]]=dict(state=fields[1],exit_code='unknown',elapsed=fields[2],ended='',source='squeue')
    return rows


def notify(root, state, key, message, config):
    if key in state.setdefault('events', []):
        return
    event = dict(time=stamp(), key=key, message=message)
    with (root/'runs/watch/events.jsonl').open('a') as out:
        out.write(json.dumps(event)+'\n')
    state['events'].append(key)
    print(json.dumps(event), flush=True)
    # Only the pane/session captured at installation; never send-keys.
    if config.get('tmux_socket') and config.get('tmux_pane'):
        cmd = ['tmux', '-S', config['tmux_socket']]
        try:
            identity = subprocess.run(cmd + ['display-message', '-p', '-t', config['tmux_pane'], '#{session_id}'],
                                      text=True, capture_output=True, timeout=3, check=True).stdout.strip()
            if identity == config.get('tmux_session'):
                subprocess.run(cmd + ['display-message', '-t', config['tmux_pane'], message],
                               capture_output=True, timeout=3, check=True)
        except (subprocess.SubprocessError, OSError) as error:
            event['tmux_error'] = str(error)
            if getattr(error, 'stderr', None):
                stderr = error.stderr
                event['tmux_stderr'] = stderr.decode(errors='replace') if isinstance(stderr, bytes) else stderr
            # Persistent events remain available even if tmux has closed.
            with (root/'runs/watch/notification_errors.jsonl').open('a') as out:
                out.write(json.dumps(event)+'\n')


def followup(root, job, config):
    action = job.get('completion_action')
    if action not in ('summarize_comparison', 'summarize_hybrid', 'summarize_geometry', 'summarize_training_profile', 'summarize_holdout', 'summarize_pilot', 'summarize_external', 'summarize_quality', 'summarize_online', 'summarize_recovery','summarize_checkpoint','summarize_efficiency','summarize_consensus','summarize_optimizer','summarize_optimizer_state','summarize_kernels','summarize_matched_online','summarize_roundtrip','summarize_layers','summarize_state_roundtrip','summarize_ensemble','summarize_teacher_ensemble','summarize_layer_probe','summarize_conditioning','summarize_distill_data','summarize_latent_pose','summarize_distillation','summarize_ensemble_latency','summarize_label_audit','summarize_reflow_data','summarize_reflow','summarize_reflow_eval','summarize_overfit_labels','summarize_overfit','summarize_oracle_transport','summarize_teacher_recurrence','summarize_midpoint','summarize_overfit_native','summarize_tensor_precision','summarize_expanded_native','summarize_compact_condition'):
        raise ValueError('unrecognized completion action')
    ids = job_ids(job)
    if action == 'summarize_comparison' and len(ids) != 2:
        raise ValueError('comparison follow-up requires two registered tasks')
    prefix = {'summarize_hybrid': 'hybrid', 'summarize_comparison': 'comparison', 'summarize_geometry': 'geometry', 'summarize_training_profile': 'training_profile', 'summarize_holdout': 'holdout', 'summarize_pilot': 'pilot', 'summarize_external': 'external', 'summarize_quality': 'quality', 'summarize_online': 'online', 'summarize_recovery': 'recovery', 'summarize_checkpoint': 'checkpoint', 'summarize_efficiency': 'efficiency', 'summarize_consensus': 'consensus', 'summarize_optimizer': 'optimizer', 'summarize_optimizer_state': 'optimizer_state', 'summarize_kernels': 'kernels', 'summarize_matched_online': 'matched_online', 'summarize_roundtrip': 'roundtrip', 'summarize_layers': 'layers', 'summarize_state_roundtrip': 'state_roundtrip', 'summarize_ensemble': 'ensemble', 'summarize_teacher_ensemble': 'teacher_ensemble', 'summarize_layer_probe': 'layer_probe', 'summarize_conditioning': 'conditioning', 'summarize_distill_data': 'distill_data', 'summarize_latent_pose': 'latent_pose', 'summarize_distillation': 'distillation', 'summarize_ensemble_latency': 'ensemble_latency', 'summarize_label_audit': 'label_audit', 'summarize_reflow_data': 'reflow_data', 'summarize_reflow': 'reflow', 'summarize_reflow_eval': 'reflow_eval', 'summarize_overfit_labels': 'overfit_labels', 'summarize_overfit': 'overfit', 'summarize_oracle_transport': 'oracle_transport', 'summarize_teacher_recurrence': 'teacher_recurrence', 'summarize_midpoint': 'midpoint', 'summarize_overfit_native': 'overfit_native', 'summarize_tensor_precision': 'tensor_precision', 'summarize_expanded_native': 'expanded_native', 'summarize_compact_condition': 'compact_condition'}[action]
    report = root/'reports'/f"{prefix}_{job['id']}"
    command = [config['python'], str(root/'scripts'/f'{action}.py'), '--runs',
               *[str(root/'runs'/f'{prefix}_{i}') for i in ids], '--output', str(report)]
    if action == 'summarize_hybrid':
        registered = json.loads((root/'runs/jobs.json').read_text())['jobs']
        reference = next(j for j in registered if j['id'] == job['reference_job'])
        command += ['--references', *[str(root/'runs'/f'comparison_{i}') for i in job_ids(reference)]]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', PYTHONPATH=str(root/'src'))
    with (root/'runs/watch'/f"analysis_{job['id']}.log").open('a') as log:
        subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                       timeout=240, check=True)
    if action in ('summarize_ensemble','summarize_teacher_ensemble') and json.loads(report.with_suffix('.json').read_text()).get('status')=='complete':
        from start_state_scoring import start
        start(root,job['id'])
    return str(report.with_suffix('.md'))



def tick_local(root, state, config):
    """Monitor only explicitly registered project CPU units, including timeout."""
    path=root/'runs/local_jobs.json'
    if not path.exists():return []
    outstanding=[]
    for job in json.loads(path.read_text())['jobs']:
        unit=job['unit']
        if not re.fullmatch(r'esm-proae-[a-z0-9-]+\.service',unit):raise ValueError('invalid local project unit')
        entry=state.setdefault('local_jobs',{}).setdefault(unit,{})
        if entry.get('handled'):continue
        status_path=(root/job['status_path']).resolve()
        if root/'runs' not in status_path.parents:raise ValueError('local status outside runs')
        result=subprocess.run(['systemctl','--user','show',unit,'-p','ActiveState','-p','Result'],capture_output=True,text=True,check=True,timeout=10)
        fields=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        try:
            data=json.loads(status_path.read_text()) if status_path.exists() else {'status':'running'}
        except json.JSONDecodeError:
            outstanding.append(unit);continue
        if data['status']=='running' and fields.get('ActiveState') in ('active','activating'):
            outstanding.append(unit);continue
        if data['status']=='running':
            data.update(status='failed',error=f"CPU unit stopped before completion: {fields}")
            write_json(status_path,data)
        action=job['action']
        if action not in ('summarize_holdout','summarize_training_data','summarize_recovery_data','summarize_nmr_controls','summarize_state_scores','summarize_teacher_data','summarize_tm_scores'):raise ValueError('unrecognized local action')
        report=root/'reports'/job['report']
        command=[config['python'],str(root/'scripts'/f'{action}.py'),'--runs',str(status_path.parent),'--output',str(report)]
        env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
        with (root/'runs/watch'/f'analysis_{unit}.log').open('a') as log:
            subprocess.run(command,env=env,cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        entry.update(handled=True,outcome=data['status'],report=str(report.with_suffix('.md')))
        notify(root,state,f'{unit}:analyzed',f"CPU preparation {unit}: {data['status']}; report {report.with_suffix('.md')}",config)
    return outstanding

def tick(root, config, query=scheduler_states, analyze=followup):
    state_path = root/'runs/watch/state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'jobs': {}, 'events': []}
    state.setdefault('jobs', {})
    registry = json.loads((root/'runs/jobs.json').read_text())
    all_ids = [i for job in registry['jobs'] for i in job_ids(job)]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError('duplicate registry ownership')
    pending = []
    for job in registry['jobs']:
        entry = state['jobs'].get(job['id'], {})
        if entry.get('handled'):
            continue
        # Historical terminal jobs without a requested follow-up need no polling.
        if job.get('state') in TERMINAL and not job.get('completion_action'):
            continue
        pending.append(job)
    requested = [i for job in pending for i in job_ids(job)]
    rows = query(requested) if requested else {}
    for job in pending:
        jid = job['id']
        entry = state['jobs'].setdefault(jid, {})
        ids = job_ids(job)
        entry['tasks'] = {i: rows.get(i, {'state': 'UNKNOWN'}) for i in ids}
        missing = [i for i in ids if i not in rows]
        if missing:
            entry['unknown_since'] = entry.get('unknown_since', time.time())
            if time.time()-entry['unknown_since'] > 300:
                notify(root, state, f'{jid}:unknown', f'ESM project: scheduler has no record for {missing}; watcher is retrying.', config)
            continue
        entry.pop('unknown_since', None)
        for i in ids:
            r = rows[i]
            if r['state'] in TERMINAL:
                notify(root, state, f"{i}:{r['state']}:{r['exit_code']}",
                       f"ESM project job {i}: {r['state']}, exit {r['exit_code']}, elapsed {r['elapsed']}.", config)
        if not all(rows[i]['state'] in TERMINAL for i in ids):
            continue
        success = all(rows[i]['state'] == 'COMPLETED' and rows[i]['exit_code'] == '0:0' for i in ids)
        if not success and job.get('completion_action') not in ('summarize_hybrid', 'summarize_geometry', 'summarize_training_profile', 'summarize_holdout', 'summarize_pilot', 'summarize_external', 'summarize_quality', 'summarize_online', 'summarize_recovery','summarize_checkpoint','summarize_efficiency','summarize_consensus','summarize_optimizer','summarize_optimizer_state','summarize_kernels','summarize_matched_online','summarize_roundtrip','summarize_layers','summarize_state_roundtrip','summarize_ensemble','summarize_teacher_ensemble','summarize_layer_probe','summarize_conditioning','summarize_distill_data','summarize_latent_pose','summarize_distillation','summarize_ensemble_latency','summarize_label_audit','summarize_reflow_data','summarize_reflow','summarize_reflow_eval','summarize_overfit_labels','summarize_overfit','summarize_oracle_transport','summarize_teacher_recurrence','summarize_midpoint','summarize_overfit_native','summarize_tensor_precision','summarize_expanded_native','summarize_compact_condition'):
            entry.update(handled=True, outcome='job_failed', handled_at=stamp())
        elif not job.get('completion_action'):
            entry.update(handled=True, outcome='completed', handled_at=stamp())
        elif time.time() >= entry.get('retry_after', 0):
            # Save completion detection before a potentially expensive follow-up.
            write_json(state_path, state)
            try:
                report = analyze(root, job, config)
                entry.update(handled=True, outcome='analyzed', report=report, handled_at=stamp())
                notify(root, state, f'{jid}:analyzed', f'ESM project {jid}: automatic analysis ready at {report}', config)
            except Exception as error:
                attempts = entry.get('attempts', 0)+1
                entry.update(attempts=attempts, analysis_error=str(error), retry_after=time.time()+min(900, 60*2**min(attempts, 4)))
                notify(root, state, f'{jid}:analysis_failed', f'ESM project {jid}: analysis failed; see runs/watch/analysis_{jid}.log; automatic retries enabled.', config)
    state['outstanding_local_units']=tick_local(root,state,config)
    from overfit_checkpoint_analysis import tick as checkpoint_tick
    for key,message in checkpoint_tick(root,state,registry,config):
        notify(root,state,key,message,config)
    state.update(last_successful_check=stamp(), host=socket.gethostname(),
                 outstanding_jobs=[j['id'] for j in pending if not state['jobs'].get(j['id'], {}).get('handled')])
    write_json(state_path, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    a = parser.parse_args()
    root = a.root.resolve()
    directory = root/'runs/watch'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory/'lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        config = json.loads((directory/'config.json').read_text())
        try:
            state = tick(root, config)
            write_json(directory/'heartbeat.json', dict(checked_at=stamp(), status='ok', host=socket.gethostname(),
                       outstanding_jobs=state['outstanding_jobs'],outstanding_local_units=state.get('outstanding_local_units',[])))
        except Exception as error:
            write_json(directory/'heartbeat.json', dict(checked_at=stamp(), status='error', error=str(error), host=socket.gethostname()))
            state_path = directory/'state.json'
            state = json.loads(state_path.read_text()) if state_path.exists() else {'events': []}
            notify(root, state, f'watcher_error:{type(error).__name__}', f'ESM project watcher error: {error}', config)
            write_json(state_path, state)
            raise


if __name__ == '__main__':
    main()
