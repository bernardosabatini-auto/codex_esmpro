"""Submit only this project's jobs, enforce its GPU cap, register immediately."""
import argparse,datetime,fcntl,json,subprocess
from pathlib import Path
import watch_jobs as watch
from submission_snapshot import freeze_submission


def policy_deadline(permission,now,minutes):
 """Standing authorization does not override a later user-specified deadline."""
 if permission.get('status')!='active' or permission.get('mode')!='experiment_bounded' or permission.get('max_total_gpus')!=8:
  raise RuntimeError('invalid or inactive experiment execution policy')
 deadline=datetime.datetime.fromisoformat(permission['deadline_utc']) if permission.get('deadline_utc') else None
 if deadline and now+datetime.timedelta(minutes=minutes,seconds=120)>deadline:
  raise RuntimeError('requested walltime extends beyond the authorized deadline')
 return deadline


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--script',required=True);p.add_argument('--purpose',required=True)
 p.add_argument('--gpus-per-task',type=int,default=1);p.add_argument('--tasks',type=int,default=1)
 p.add_argument('--minutes',type=int,required=True);p.add_argument('--action',required=True)
 a=p.parse_args();root=Path(__file__).resolve().parents[1]
 if not 0<=a.gpus_per_task<=8 or not 1<=a.tasks<=8 or a.gpus_per_task*a.tasks>8:raise ValueError('invalid resource request')
 if a.action not in ('summarize_geometry','summarize_training_profile','summarize_holdout','summarize_pilot','summarize_external','summarize_quality','summarize_online','summarize_recovery','summarize_checkpoint','summarize_efficiency','summarize_consensus','summarize_optimizer','summarize_optimizer_state','summarize_kernels','summarize_matched_online','summarize_roundtrip','summarize_layers','summarize_state_roundtrip','summarize_ensemble','summarize_teacher_ensemble','summarize_layer_probe','summarize_conditioning','summarize_distill_data','summarize_latent_pose','summarize_distillation','summarize_ensemble_latency','summarize_label_audit','summarize_reflow_data','summarize_reflow','summarize_reflow_eval','summarize_overfit_labels','summarize_overfit','summarize_oracle_transport','summarize_teacher_recurrence','summarize_midpoint','summarize_overfit_native','summarize_tensor_precision','summarize_expanded_native','summarize_compact_condition','summarize_decoder_steps','summarize_compact_native','summarize_student_extension','summarize_expansion_data','summarize_expansion_native','summarize_confidence_chunks','summarize_latent_repair','summarize_cuda_graph','summarize_teacher_summary','summarize_summary_features','summarize_replay_native','summarize_bounded_retry_native','summarize_retry_ensemble','summarize_retry_prefix'):raise ValueError('unsupported completion action')
 script=(root/a.script).resolve()
 if script.parent!=root/'slurm':raise ValueError('script must be in project slurm folder')
 with (root/'runs/submit.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  subprocess.run(['systemctl','--user','is-active','--quiet','esm-proae-reboot-watch.timer'],check=True)
  beat=json.loads((root/'runs/watch/heartbeat.json').read_text());now=datetime.datetime.now(datetime.timezone.utc)
  if beat['status']!='ok' or (now-datetime.datetime.fromisoformat(beat['checked_at'])).total_seconds()>=120:raise RuntimeError('watcher heartbeat stale')
  path=root/'runs/jobs.json';registry=json.loads(path.read_text())
  outstanding=[j for j in registry['jobs'] if j.get('state') not in watch.TERMINAL]
  ids=[i for j in outstanding for i in watch.job_ids(j)];states=watch.scheduler_states(ids) if ids else {}
  count=sum(j.get('gpus_per_task',j['gpus']//len(watch.job_ids(j)))*sum(states.get(i,{}).get('state') not in watch.TERMINAL for i in watch.job_ids(j)) for j in outstanding)
  if count+a.gpus_per_task*a.tasks>8:raise RuntimeError('project GPU cap would be exceeded')
  window=root/'runs/autonomous_20261001.json';deadline=None
  policy=root/'runs/execution_policy.json'
  if policy.exists():
   permission=json.loads(policy.read_text())
   deadline=policy_deadline(permission,now,a.minutes)
  elif window.exists():
   execution=json.loads(window.read_text())
   if execution['status']!='active':
    raise RuntimeError('autonomous execution window is not active; refusing late submission')
   if execution['status']=='active':
    deadline=datetime.datetime.fromisoformat(execution['deadline'].replace('Z','+00:00'))
    if now+datetime.timedelta(minutes=a.minutes,seconds=120)>deadline:
     raise RuntimeError('requested walltime extends beyond the autonomous execution window')
  commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
  submitted_script,snapshot=freeze_submission(root,script,commit)
  command=['sbatch','--parsable',f'--gres=gpu:{a.gpus_per_task}',f'--time={a.minutes}'] if a.gpus_per_task else ['sbatch','--parsable',f'--time={a.minutes}']
  if deadline:command.append('--deadline='+deadline.astimezone().strftime('%Y-%m-%dT%H:%M:%S'))
  if a.tasks>1:command += [f'--array=0-{a.tasks-1}%{a.tasks}']
  result=subprocess.run(command+[str(submitted_script)],cwd=root,text=True,capture_output=True)
  if result.returncode:raise RuntimeError(result.stderr.strip())
  jid=result.stdout.strip().split(';')[0]
  if not jid.isdigit():raise RuntimeError(f'unexpected submission result {result.stdout!r}')
  job=dict(id=jid,purpose=a.purpose,gpus=a.gpus_per_task*a.tasks,gpus_per_task=a.gpus_per_task,
    time_limit_minutes=a.minutes,submitted=now.isoformat(),script=a.script,state='SUBMITTED',
    completion_action=a.action,code_commit=commit,code_snapshot=str(snapshot))
  if deadline:job['deadline_utc']=deadline.isoformat()
  if policy.exists():job['execution_policy']=json.loads(policy.read_text())
  if a.tasks>1:job['tasks']=[f'{jid}_{i}' for i in range(a.tasks)]
  registry['jobs'].append(job);watch.write_json(path,registry)
  print(json.dumps(dict(submitted=jid,total_requested_gpus=count+a.gpus_per_task*a.tasks)))

if __name__=='__main__':main()
