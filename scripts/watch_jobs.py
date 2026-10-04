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
    # Query only exact owned IDs. A purged single ID is absent from the live
    # controller only when it explicitly says invalid ID and accounting is final.
    # Other failures still propagate; mixed lists are checked one ID at a time.
    def live_rows(owned):
        try:
            return run(['squeue','-h','-r','-j',','.join(owned),'--format=%i|%T|%M'],
                       capture_output=True,text=True,timeout=20,check=True).stdout
        except subprocess.CalledProcessError as error:
            if (error.stderr or '').strip() != 'slurm_load_jobs error: Invalid job id specified' or (error.stdout or '').strip():
                raise
            if len(owned)>1:
                return '\n'.join(live_rows([ident]) for ident in owned)
            if rows.get(owned[0],{}).get('state') not in TERMINAL:
                raise
            return ''
    if ids:
        for line in live_rows(ids).splitlines():
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


def refresh_analysis_monitoring(root, query=scheduler_states):
    """Perform a real owned-job poll while a long CPU audit is in progress."""
    root = Path(root)
    registry = json.loads((root/'runs/jobs.json').read_text())
    state_path = root/'runs/watch/state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    ids = [i for job in registry['jobs']
           if not state.get('jobs', {}).get(job['id'], {}).get('handled')
           and not (job.get('state') in TERMINAL and not job.get('completion_action'))
           for i in job_ids(job)]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate registry ownership')
    rows = query(ids) if ids else {}
    # Query failure propagates; never refresh freshness merely for being alive.
    write_json(root/'runs/watch/heartbeat.json', dict(
        checked_at=stamp(), status='ok', host=socket.gethostname(),
        outstanding_jobs=[i for i in ids if rows.get(i, {}).get('state') not in TERMINAL],
        outstanding_local_units=state.get('outstanding_local_units', []),
        cpu_analysis_in_progress=True))


def run_monitored_analysis(command, *, root, env, log, timeout=240):
    deadline = time.monotonic() + timeout
    with subprocess.Popen(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT) as child:
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                try:
                    code = child.wait(timeout=min(30, remaining))
                except subprocess.TimeoutExpired:
                    refresh_analysis_monitoring(root)
                    continue
                if code:
                    raise subprocess.CalledProcessError(code, command)
                return
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()


def followup(root, job, config):
    action = job.get('completion_action')
    if action not in ('summarize_comparison', 'summarize_hybrid', 'summarize_geometry', 'summarize_training_profile', 'summarize_holdout', 'summarize_pilot', 'summarize_external', 'summarize_quality', 'summarize_online', 'summarize_recovery','summarize_checkpoint','summarize_efficiency','summarize_consensus','summarize_optimizer','summarize_optimizer_state','summarize_kernels','summarize_matched_online','summarize_roundtrip','summarize_layers','summarize_state_roundtrip','summarize_ensemble','summarize_teacher_ensemble','summarize_layer_probe','summarize_conditioning','summarize_distill_data','summarize_latent_pose','summarize_distillation','summarize_ensemble_latency','summarize_label_audit','summarize_reflow_data','summarize_reflow','summarize_reflow_eval','summarize_overfit_labels','summarize_overfit','summarize_oracle_transport','summarize_teacher_recurrence','summarize_midpoint','summarize_overfit_native','summarize_tensor_precision','summarize_expanded_native','summarize_compact_condition','summarize_decoder_steps','summarize_compact_native','summarize_student_extension','summarize_expansion_data','summarize_expansion_native','summarize_confidence_chunks','summarize_latent_repair','summarize_cuda_graph','summarize_teacher_summary','summarize_summary_features','summarize_replay_native','summarize_bounded_retry_native','summarize_retry_ensemble','summarize_retry_prefix','summarize_generative_pilot','summarize_designability','summarize_unconditional_labels','summarize_unconditional_reflow','summarize_noise_guidance','summarize_noise_designability','summarize_isolated_motif','summarize_fragment_designability','summarize_fixed_motif_designability','summarize_motif_noise_guidance','summarize_motif_history','summarize_conditional_coupling','summarize_conditional_coupling_pair','summarize_conditional_coupling_native','summarize_fragment_data','summarize_fragment_training','summarize_trained_fragment_designability','summarize_fragment_fixed_positive','summarize_fragment_geometry_pose','summarize_fragment_guidance','summarize_fragment_feedback','summarize_roundtrip_designability','summarize_fragment_frame','summarize_fragment_target_frame','summarize_fragment_frame_calibration','summarize_fragment_frame_confirmation','summarize_fragment_strict_followup','summarize_fragment_repetition','summarize_fragment_refinement','summarize_fragment_full_backbone','summarize_fragment_validation','summarize_fragment_validation_refold','summarize_fragment_endpoint_guidance','summarize_fragment_teacher_augmentation','summarize_fragment_endpoint_refold','summarize_extra_fragment_data','summarize_extra_fragment_validation','summarize_extra_fragment_refold','summarize_broad_fragment_data','summarize_broad_codec_batch','summarize_broad_fragment_full','summarize_fragment_source_refold','summarize_fragment_preference_refold','summarize_native_anchor_training','summarize_native_positive_decode','summarize_decoder_fragment_variance','summarize_masked_fragment_training','summarize_pretrained_masked_training','summarize_scaffold_clock_training','summarize_fragment_decoder_training','summarize_fragment_decoder_fm_training','summarize_teacher_repeatability_probe'):
        raise ValueError('unrecognized completion action')
    ids = job_ids(job)
    if action == 'summarize_comparison' and len(ids) != 2:
        raise ValueError('comparison follow-up requires two registered tasks')
    prefix = {'summarize_hybrid': 'hybrid', 'summarize_comparison': 'comparison', 'summarize_geometry': 'geometry', 'summarize_training_profile': 'training_profile', 'summarize_holdout': 'holdout', 'summarize_pilot': 'pilot', 'summarize_external': 'external', 'summarize_quality': 'quality', 'summarize_online': 'online', 'summarize_recovery': 'recovery', 'summarize_checkpoint': 'checkpoint', 'summarize_efficiency': 'efficiency', 'summarize_consensus': 'consensus', 'summarize_optimizer': 'optimizer', 'summarize_optimizer_state': 'optimizer_state', 'summarize_kernels': 'kernels', 'summarize_matched_online': 'matched_online', 'summarize_roundtrip': 'roundtrip', 'summarize_layers': 'layers', 'summarize_state_roundtrip': 'state_roundtrip', 'summarize_ensemble': 'ensemble', 'summarize_teacher_ensemble': 'teacher_ensemble', 'summarize_layer_probe': 'layer_probe', 'summarize_conditioning': 'conditioning', 'summarize_distill_data': 'distill_data', 'summarize_latent_pose': 'latent_pose', 'summarize_distillation': 'distillation', 'summarize_ensemble_latency': 'ensemble_latency', 'summarize_label_audit': 'label_audit', 'summarize_reflow_data': 'reflow_data', 'summarize_reflow': 'reflow', 'summarize_reflow_eval': 'reflow_eval', 'summarize_overfit_labels': 'overfit_labels', 'summarize_overfit': 'overfit', 'summarize_oracle_transport': 'oracle_transport', 'summarize_teacher_recurrence': 'teacher_recurrence', 'summarize_midpoint': 'midpoint', 'summarize_overfit_native': 'overfit_native', 'summarize_tensor_precision': 'tensor_precision', 'summarize_expanded_native': 'expanded_native', 'summarize_compact_condition': 'compact_condition', 'summarize_decoder_steps': 'decoder_steps', 'summarize_compact_native': 'compact_native', 'summarize_student_extension': 'student_extension', 'summarize_expansion_data': 'expansion_data', 'summarize_expansion_native': 'expansion_native', 'summarize_confidence_chunks': 'confidence_chunks', 'summarize_latent_repair': 'latent_repair', 'summarize_cuda_graph': 'cuda_graph', 'summarize_teacher_summary': 'teacher_summary', 'summarize_summary_features': 'summary_features', 'summarize_replay_native': 'replay_native', 'summarize_bounded_retry_native': 'bounded_retry_native', 'summarize_retry_ensemble': 'retry_ensemble', 'summarize_retry_prefix': 'retry_prefix', 'summarize_generative_pilot': 'generative_pilot', 'summarize_designability': 'designability', 'summarize_unconditional_labels': 'unconditional_labels', 'summarize_unconditional_reflow': 'unconditional_reflow', 'summarize_noise_guidance': 'noise_guidance', 'summarize_noise_designability': 'noise_designability', 'summarize_isolated_motif': 'isolated_motif', 'summarize_fragment_designability': 'fragment_designability', 'summarize_fixed_motif_designability': 'fixed_motif_designability', 'summarize_motif_noise_guidance': 'motif_noise_guidance', 'summarize_motif_history': 'motif_history', 'summarize_conditional_coupling': 'conditional_coupling', 'summarize_conditional_coupling_pair': 'conditional_coupling', 'summarize_conditional_coupling_native': 'conditional_coupling_native', 'summarize_fragment_data': 'fragment_data', 'summarize_fragment_training': 'fragment_training', 'summarize_trained_fragment_designability': 'trained_fragment_designability', 'summarize_fragment_fixed_positive': 'fragment_fixed_positive', 'summarize_fragment_geometry_pose': 'fragment_geometry_pose', 'summarize_fragment_guidance': 'fragment_guidance', 'summarize_fragment_feedback': 'fragment_feedback', 'summarize_roundtrip_designability': 'roundtrip_designability', 'summarize_fragment_frame': 'fragment_frame', 'summarize_fragment_target_frame': 'fragment_target_frame', 'summarize_fragment_frame_calibration': 'fragment_frame_calibration', 'summarize_fragment_frame_confirmation': 'fragment_frame_confirmation', 'summarize_fragment_strict_followup': 'fragment_strict_followup', 'summarize_fragment_repetition': 'fragment_repetition', 'summarize_fragment_refinement': 'fragment_refinement', 'summarize_fragment_full_backbone': 'fragment_full_backbone', 'summarize_fragment_validation': 'fragment_validation', 'summarize_extra_fragment_validation': 'extra_fragment_validation', 'summarize_extra_fragment_refold': 'extra_fragment_refold', 'summarize_broad_fragment_data': 'broad_fragment_data', 'summarize_broad_codec_batch': 'broad_codec_batch', 'summarize_broad_fragment_full': 'broad_fragment_full', 'summarize_fragment_source_refold': 'fragment_source_refold', 'summarize_fragment_preference_refold': 'fragment_preference_refold', 'summarize_native_anchor_training': 'native_anchor_training', 'summarize_native_positive_decode': 'native_positive_decode', 'summarize_decoder_fragment_variance': 'decoder_fragment_variance', 'summarize_masked_fragment_training': 'masked_fragment_training', 'summarize_pretrained_masked_training': 'pretrained_masked_training', 'summarize_scaffold_clock_training': 'scaffold_clock_training', 'summarize_fragment_decoder_training': 'fragment_decoder_training', 'summarize_fragment_decoder_fm_training': 'fragment_decoder_fm_training', 'summarize_teacher_repeatability_probe': 'teacher_repeatability_probe', 'summarize_extra_fragment_data': 'extra_fragment_data', 'summarize_fragment_endpoint_refold': 'fragment_endpoint_refold', 'summarize_fragment_validation_refold': 'fragment_validation_refold', 'summarize_fragment_endpoint_guidance': 'fragment_endpoint_guidance','summarize_fragment_teacher_augmentation': 'fragment_teacher_augmentation'}[action]
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
        run_monitored_analysis(command, root=root, env=env, log=log, timeout=900 if action=='summarize_fragment_preference_refold' else 240)
        if action == 'summarize_native_anchor_training':
            from compare_native_anchor_training import ready_command
            comparison = ready_command(root)
            if comparison:
                run_monitored_analysis([config['python'], *comparison], root=root, env=env, log=log, timeout=240)
        if action == 'summarize_fragment_preference_refold':
            from compare_fragment_preferences import ready_command
            comparison = ready_command(root)
            if comparison:
                run_monitored_analysis([config['python'], *comparison], root=root, env=env, log=log, timeout=900)
        if action == 'summarize_fragment_source_refold':
            from compare_fragment_source_refolds import ready_command
            comparison = ready_command(root)
            if comparison:
                run_monitored_analysis([config['python'], *comparison], root=root, env=env, log=log, timeout=240)
    if action in ('summarize_ensemble','summarize_teacher_ensemble','summarize_retry_ensemble') and json.loads(report.with_suffix('.json').read_text()).get('status')=='complete':
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
    analyses_started = 0
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
        if not success and job.get('completion_action') not in ('summarize_hybrid', 'summarize_geometry', 'summarize_training_profile', 'summarize_holdout', 'summarize_pilot', 'summarize_external', 'summarize_quality', 'summarize_online', 'summarize_recovery','summarize_checkpoint','summarize_efficiency','summarize_consensus','summarize_optimizer','summarize_optimizer_state','summarize_kernels','summarize_matched_online','summarize_roundtrip','summarize_layers','summarize_state_roundtrip','summarize_ensemble','summarize_teacher_ensemble','summarize_layer_probe','summarize_conditioning','summarize_distill_data','summarize_latent_pose','summarize_distillation','summarize_ensemble_latency','summarize_label_audit','summarize_reflow_data','summarize_reflow','summarize_reflow_eval','summarize_overfit_labels','summarize_overfit','summarize_oracle_transport','summarize_teacher_recurrence','summarize_midpoint','summarize_overfit_native','summarize_tensor_precision','summarize_expanded_native','summarize_compact_condition','summarize_decoder_steps','summarize_compact_native','summarize_student_extension','summarize_expansion_data','summarize_expansion_native','summarize_confidence_chunks','summarize_latent_repair','summarize_cuda_graph','summarize_teacher_summary','summarize_summary_features','summarize_replay_native','summarize_bounded_retry_native','summarize_retry_ensemble','summarize_retry_prefix','summarize_generative_pilot','summarize_designability','summarize_unconditional_labels','summarize_unconditional_reflow','summarize_noise_guidance','summarize_noise_designability','summarize_isolated_motif','summarize_fragment_designability','summarize_fixed_motif_designability','summarize_motif_noise_guidance','summarize_motif_history','summarize_conditional_coupling','summarize_conditional_coupling_pair','summarize_conditional_coupling_native','summarize_fragment_data','summarize_fragment_training','summarize_trained_fragment_designability','summarize_fragment_fixed_positive','summarize_fragment_geometry_pose','summarize_fragment_guidance','summarize_fragment_feedback','summarize_roundtrip_designability','summarize_fragment_frame','summarize_fragment_target_frame','summarize_fragment_frame_calibration','summarize_fragment_frame_confirmation','summarize_fragment_strict_followup','summarize_fragment_repetition','summarize_fragment_refinement','summarize_fragment_full_backbone','summarize_fragment_validation','summarize_fragment_validation_refold','summarize_fragment_endpoint_guidance','summarize_fragment_teacher_augmentation','summarize_fragment_endpoint_refold','summarize_extra_fragment_data','summarize_extra_fragment_validation','summarize_extra_fragment_refold','summarize_broad_fragment_data','summarize_broad_codec_batch','summarize_broad_fragment_full','summarize_fragment_source_refold','summarize_fragment_preference_refold','summarize_native_anchor_training','summarize_native_positive_decode','summarize_decoder_fragment_variance','summarize_masked_fragment_training','summarize_pretrained_masked_training','summarize_scaffold_clock_training','summarize_fragment_decoder_training','summarize_fragment_decoder_fm_training','summarize_teacher_repeatability_probe'):
            entry.update(handled=True, outcome='job_failed', handled_at=stamp())
        elif not job.get('completion_action'):
            entry.update(handled=True, outcome='completed', handled_at=stamp())
        elif time.time() >= entry.get('retry_after', 0) and analyses_started < 1:
            analyses_started += 1
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
    # This fixed comparison also depends on independent CPU diversity audits;
    # they can finish after the final GPU completion callback has returned.
    if analyses_started == 0:
        from compare_native_anchor_models import ready_command as ready_native_models
        from compare_native_positive_models import ready_command as ready_positive_models
        from compare_pretrained_masked_models import ready_command as ready_masked_models
        from compare_scaffold_clock_models import ready_command as ready_clock_models
        from compare_fragment_decoder_models import ready_command as ready_decoder_models
        from compare_fragment_decoder_fm_models import ready_command as ready_decoder_fm_models
        command = ready_native_models(root) or ready_positive_models(root) or ready_masked_models(root) or ready_clock_models(root) or ready_decoder_models(root) or ready_decoder_fm_models(root)
        if command:
            env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', PYTHONPATH=str(root/'src'))
            with (root/'runs/watch/native_anchor_model_comparison.log').open('a') as log:
                run_monitored_analysis([config['python'], *command], root=root, env=env, log=log, timeout=900)
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
