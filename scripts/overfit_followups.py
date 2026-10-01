"""Advance only the declared label -> profile -> three-arm capacity graph."""
import datetime,fcntl,json,os,subprocess
from pathlib import Path
from prepare_overfit import sha
from watch_jobs import write_json,TERMINAL

ROOT=Path(__file__).resolve().parents[1]
PYTHON='/n/home08/bsabatini/.conda/envs/proteinae/bin/python'
TIMER='esm-proae-overfit-followups.timer'


def tick():
    plan=json.loads((ROOT/'runs/overfit_followups.json').read_text());state_path=ROOT/'runs/overfit_followups_state.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else dict(status='waiting',events=[])
    now=datetime.datetime.now(datetime.timezone.utc);state['checked_at']=now.isoformat()
    def finish(status,reason=None):
        state['status']=status
        if reason:state['reason']=reason
        write_json(state_path,state)
        subprocess.run(['systemctl','--user','stop',TIMER],check=True)
    policy=json.loads((ROOT/'runs/execution_policy.json').read_text())
    if policy.get('status')!='active' or now>=datetime.datetime.fromisoformat(plan['deadline_utc']):finish('stopped','Authorization inactive or deadline reached');return
    jobs=json.loads((ROOT/'runs/jobs.json').read_text())['jobs'];byid={j['id']:j for j in jobs}
    parent=byid[plan['label_job']]
    if parent['completion_action']!='summarize_overfit_labels':raise ValueError('invalid registered label parent')
    label_path=ROOT/f"runs/overfit_labels_{plan['label_job']}/manifest.json"
    if not label_path.exists():write_json(state_path,state);return
    label=json.loads(label_path.read_text())
    if label['status']=='failed':finish('label_failed',label.get('error'));return
    if label['status']!='complete':write_json(state_path,state);return
    if label['config']['protocol_sha256']!=plan['protocol_sha256']:raise ValueError('unexpected label protocol')
    if not label['training_gate_passed']:finish('label_gate_failed','Reconstruction gate failed; no training');return
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONPATH=str(ROOT/'src'))
    def prepare(extra,output):
        subprocess.run([PYTHON,str(ROOT/'scripts/prepare_overfit_training.py'),'--labels',str(label_path),'--output',str(ROOT/output),*extra],cwd=ROOT,env=env,check=True,timeout=60)
    def submit(script,purpose,minutes):
        result=subprocess.run([PYTHON,str(ROOT/'scripts/submit_registered.py'),'--script',script,'--purpose',purpose,'--minutes',str(minutes),'--action','summarize_overfit'],cwd=ROOT,env=env,check=True,text=True,capture_output=True,timeout=120)
        ident=json.loads(result.stdout.strip().splitlines()[-1])['submitted'];state['events'].append(dict(time=now.isoformat(),job=ident,purpose=purpose));write_json(state_path,state);return ident
    prefix=plan['purpose_prefix'];profile=[j for j in jobs if j['purpose']==prefix+' profile']
    if len(profile)>1:raise ValueError('duplicate capacity profile')
    if not profile:
        prepare([], 'runs/overfit_profile.json');state['profile_job']=submit('slurm/overfit_profile_h200.sbatch',prefix+' profile',10);state['status']='profile_submitted';write_json(state_path,state);return
    profile=profile[0];state['profile_job']=profile['id'];report=ROOT/f"reports/overfit_{profile['id']}.json"
    if not report.exists():
        if profile.get('state') in TERMINAL and profile.get('state')!='COMPLETED':finish('profile_failed','Registered profile terminated unsuccessfully');return
        write_json(state_path,state);return
    result=json.loads(report.read_text())
    if result['status']!='complete' or not result['profile_only'] or result['max_reserved_gib']>110:finish('profile_gate_failed','Capacity profile failed');return
    state.setdefault('training_jobs',{})
    # Once one arm is submitted, scientific code must remain identical for the other arms.
    fingerprint=subprocess.check_output(['git','rev-parse','HEAD:src','HEAD:scripts','HEAD:slurm'],cwd=ROOT,text=True).strip()
    if state.get('training_code_trees') and state['training_code_trees']!=fingerprint:raise ValueError('scientific code changed during matched submissions')
    for arm in ('reference','aligned_teacher','pca_teacher'):
        matches=[j for j in jobs if j['purpose']==prefix+' '+arm]
        if len(matches)>1:raise ValueError('duplicate training arm')
        if matches:state['training_jobs'][arm]=matches[0]['id'];continue
        state['training_code_trees']=fingerprint;write_json(state_path,state)
        prepare(['--profile',str(report)],'runs/overfit.json')
        state['training_jobs'][arm]=submit(f'slurm/overfit_{arm}_h200.sbatch',prefix+' '+arm,115);state['status']='training_submissions';write_json(state_path,state);return
    finish('all_submitted')


def main():
    with (ROOT/'runs/overfit_followups.lock').open('w') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        try:tick()
        except Exception as error:
            path=ROOT/'runs/overfit_followups_state.json';state=json.loads(path.read_text()) if path.exists() else {};state.update(last_error=f'{type(error).__name__}: {error}',error_at=datetime.datetime.now(datetime.timezone.utc).isoformat());write_json(path,state);raise

if __name__=='__main__':main()
