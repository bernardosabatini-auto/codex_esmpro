"""One bounded watcher tick: inspect only registered jobs and run fixed CPU follow-ups.

Run every minute via the project systemd timer. Does not submit/cancel jobs,
start agents, type into tmux, or modify the job registry.
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
    if job.get('completion_action') != 'summarize_comparison':
        raise ValueError('unrecognized completion action')
    ids = job_ids(job)
    if len(ids) != 2:
        raise ValueError('comparison follow-up requires two registered tasks')
    report = root/'reports'/f"comparison_{job['id']}"
    command = [config['python'], str(root/'scripts/summarize_comparison.py'), '--runs',
               *[str(root/'runs'/f'comparison_{i}') for i in ids], '--output', str(report)]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', PYTHONPATH=str(root/'src'))
    with (root/'runs/watch'/f"analysis_{job['id']}.log").open('a') as log:
        subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                       timeout=240, check=True)
    return str(report.with_suffix('.md'))


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
        if not success:
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
                       outstanding_jobs=state['outstanding_jobs']))
        except Exception as error:
            write_json(directory/'heartbeat.json', dict(checked_at=stamp(), status='error', error=str(error), host=socket.gethostname()))
            state_path = directory/'state.json'
            state = json.loads(state_path.read_text()) if state_path.exists() else {'events': []}
            notify(root, state, f'watcher_error:{type(error).__name__}', f'ESM project watcher error: {error}', config)
            write_json(state_path, state)
            raise


if __name__ == '__main__':
    main()
