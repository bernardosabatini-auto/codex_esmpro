"""Bind the time-only contrast and audit unchanged primary random streams."""
import json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit_config(c):
    for key in ('time_protocol','time_baseline_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed time contrast provenance')
    spec=json.loads(Path(c['time_protocol']).read_text());path=Path(c['time_baseline_manifest']);base=json.loads(path.read_text())
    if path.parent.name!=spec['baseline'] or base['status']!='complete' or base['updates']!=spec['updates'] or base['config'].get('conditional_time_shift') or c.get('conditional_time_shift')!=spec['conditional_time_shift'] or spec['conditional_time_shift']!=-1:raise ValueError('Wrong time contrast')
    operational={'profile_only','updates','evaluation_steps','work_cap_seconds','allocation_minutes','profile_report','profile_report_sha256','latent_weight_profile_audit'}
    for key,value in base['config'].items():
        if key not in operational and c.get(key)!=value:raise ValueError('Changed time-only recipe: '+key)
    if c['updates']!=(40 if c['profile_only'] else spec['updates']) or c['evaluation_steps']!=([40] if c['profile_only'] else [500,2000]):raise ValueError('Changed time exposure')
    if any(c.get(k) for k in ('extension_protocol','weight_breadth_protocol','rollout_motif','auxiliary_motif','target_frame_training','backbone_tokens','fragment_representation','sampling_control_mode')):raise ValueError('Undeclared additional contrast')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if not p['profile_qualified'] or p['config']['time_protocol_sha256']!=c['time_protocol_sha256'] or not c.get('time_profile_audit'):raise ValueError('Unqualified time profile')
    return spec


def matched_traces(base,new):
    keys=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    if len(base)!=len(new) or len(base) not in (40,2000):raise ValueError('Incomplete time comparison')
    changed=0
    for x,y in zip(base,new):
        if any(x[k]!=y[k] for k in keys) or x['time_sha256']!=y['base_time_sha256'] or y['null_time_max_abs']!=0:raise ValueError('Changed non-time draw or null time')
        differs=x['time_sha256']!=y['time_sha256']
        if differs!=(y['conditioned_examples']>0):raise ValueError('Shift changed an all-null batch or missed conditions')
        changed+=differs
    if changed==0:raise ValueError('Conditional time shift missing')
    return changed


def compare(root,run):
    root,run=Path(root),Path(run);path=run/'manifest.json';new=json.loads(path.read_text());c=new['config'];spec=audit_config(c);basepath=root/'runs'/(spec['baseline_profile'] if c['profile_only'] else spec['baseline'])/'manifest.json';base=json.loads(basepath.read_text())
    if new['status']!='complete' or base['status']!='complete' or new['updates']!=c['updates'] or base['updates']!=new['updates'] or new['adapter_initial']!=base['adapter_initial'] or new['frozen_initial']!=base['frozen_initial']:raise ValueError('Incomplete or changed initialization')
    changed=matched_traces(base['training'],new['training']);same=0
    with h5py.File(basepath.parent/'evaluation_0.h5') as left,h5py.File(run/'evaluation_0.h5') as right:
        for cohort in (('development',) if c['profile_only'] else ('train','development')):
            for mode in ('conditioned','null'):
                if set(left[cohort+'/'+mode])!=set(right[cohort+'/'+mode]):raise ValueError('Changed initial inventory')
                for ident in left[cohort+'/'+mode]:
                    for key in ('latent','backbone'):
                        name=f'{cohort}/{mode}/{ident}/{key}'
                        if not np.array_equal(left[name][:],right[name][:]):raise ValueError('Changed initial outputs')
                    same+=4
    if same!=(32 if c['profile_only'] else 384):raise ValueError('Missing initial controls')
    return dict(status='complete',matched_primary_steps=len(base['training']),transformed_time_steps=changed,identical_initial_samples=same,baseline_manifest_sha256=sha(basepath),candidate_manifest_sha256=sha(path),null_times_unchanged=True)
