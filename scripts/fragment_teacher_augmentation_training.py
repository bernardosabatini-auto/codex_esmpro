"""Bind the target-only contrast and replay every endpoint assignment."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher_endpoint_pool import TeacherEndpointPool
from prepare_overfit import sha
from compare_fragment_extension import TRACE

OPERATIONAL={'profile_only','updates','evaluation_steps','work_cap_seconds','allocation_minutes','profile_report','profile_report_sha256'}


def digest(x):return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def audit_config(c):
    for key in ('augmentation_protocol','augmentation_manifest','augmentation_report','augmentation_targets','augmentation_baseline_config','augmentation_baseline_profile'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed target-augmentation source '+key)
    spec=json.loads(Path(c['augmentation_protocol']).read_text());m=json.loads(Path(c['augmentation_manifest']).read_text());d=json.loads(Path(c['augmentation_report']).read_text());base=json.loads(Path(c['augmentation_baseline_config']).read_text())
    if m['status']!='complete' or d['status']!='complete' or not d['training_gate_passed'] or d['manifest_sha256']!=c['augmentation_manifest_sha256'] or m['targets_sha256']!=c['augmentation_targets_sha256'] or c['fragments_sha256']!=m['config']['fragments_sha256'] or m['config']['protocol_sha256']!=c['augmentation_protocol_sha256'] or spec['mixture_probability']!=.5:raise ValueError('Unqualified target pool')
    if Path(c['warm_parent_manifest']).parent.name!=spec['parent'] or c['extension_arm']!='weighted' or base['profile_only'] or base['updates']!=2000 or c['seed']!=spec.get('training_seed',2026100281):raise ValueError('Wrong matched training parent')
    if spec.get('training_protein_count')==512 and ('augmentation_baseline_run' not in c or not Path(c['augmentation_baseline_run']).name.startswith('fragment_training_')):raise ValueError('Missing matched breadth control')
    if any(c.get(k)!=v for k,v in base.items() if k not in OPERATIONAL):raise ValueError('Changed non-target training recipe')
    if c['updates']!=(40 if c['profile_only'] else 2000) or c['evaluation_steps']!=([40] if c['profile_only'] else [500,2000]):raise ValueError('Changed exposure')
    if any(c.get(k) for k in ('target_frame_training','time_protocol','rollout_motif','auxiliary_motif','backbone_tokens','fragment_representation')):raise ValueError('Additional undeclared intervention')
    profile=json.loads(Path(c['augmentation_baseline_profile']).read_text())
    if profile['status']!='complete' or profile['updates']!=40 or any(profile['config'].get(k)!=v for k,v in base.items() if k not in OPERATIONAL):raise ValueError('Wrong control profile')
    if not c['profile_only']:
        pd=json.loads(Path(c['profile_report']).read_text())
        if not pd['profile_qualified'] or not pd.get('augmentation_contrast_audit') or pd['config']['augmentation_targets_sha256']!=c['augmentation_targets_sha256']:raise ValueError('Missing augmentation profile')
    return spec


def compare(root,run):
    root,run=Path(root),Path(run);path=run/'manifest.json';m=json.loads(path.read_text());c=m['config'];spec=audit_config(c)
    basepath=Path(c['augmentation_baseline_profile']) if c['profile_only'] else (Path(c['augmentation_baseline_run'])/'manifest.json' if c.get('augmentation_baseline_run') else root/'runs'/spec['matched_control']/'manifest.json');base=json.loads(basepath.read_text())
    if m['status']!='complete' or base['status']!='complete' or m['updates']!=base['updates'] or m['adapter_initial']!=base['adapter_initial'] or m['frozen_initial']!=base['frozen_initial']:raise ValueError('Incomplete matched endpoint comparison')
    if len(m['training'])!=c['updates'] or any(any(x[k]!=y[k] for k in TRACE) for x,y in zip(base['training'],m['training'])):raise ValueError('Changed primary random draws')
    if any(base['config'].get(k)!=v for k,v in json.loads(Path(c['augmentation_baseline_config']).read_text()).items() if k not in OPERATIONAL):raise ValueError('Changed actual control configuration')
    same=0
    with h5py.File(basepath.parent/'evaluation_0.h5') as left,h5py.File(run/'evaluation_0.h5') as right:
        for cohort in (('development',) if c['profile_only'] else ('train','development')):
            for mode in ('conditioned','null'):
                if set(left[cohort+'/'+mode])!=set(right[cohort+'/'+mode]):raise ValueError('Different initial coverage')
                for ident in left[cohort+'/'+mode]:
                    for key in ('latent','backbone'):
                        name=f'{cohort}/{mode}/{ident}/{key}'
                        if not np.array_equal(left[name][:],right[name][:]):raise ValueError('Different initial predictions')
                    same+=4
    pool=TeacherEndpointPool(c['augmentation_targets'],spec['seed']);traces=m['augmentation_target_updates'];applied=0
    if len(traces)!=c['updates'] or same!=(32 if c['profile_only'] else 384):raise ValueError('Incomplete initialization or target trace')
    with h5py.File(c['fragments']) as fr:
        references={i:torch.from_numpy(g['reference_z'][:]) for i,g in fr['train'].items()}
    for r,t in zip(m['training'],traces):
        reference=torch.zeros(r['batch'],r['length'],8)
        for k,ident in enumerate(r['ids']):reference[k,:len(references[ident])]=references[ident]
        target,selected=pool.draw(r['ids'],r['conditions'],reference);drop=torch.tensor(t['dropped_slots'],dtype=torch.bool);actual=torch.where(drop[:,None,None],reference,target)
        if t['step']!=r['step'] or selected!=t['candidate_indices'] or digest(drop)!=r['drop_sha256'] or digest(reference)!=t['null_target_sha256'] or digest(target)!=t['conditioned_target_sha256'] or digest(actual)!=t['selected_target_sha256']:raise ValueError('Changed endpoint choice or dropped-condition target')
        applied+=sum(k>=0 and not dropped for k,dropped in zip(selected,t['dropped_slots']))
    if applied==0:raise ValueError('No augmented conditional endpoints used')
    return dict(status='complete',matched_primary_steps=c['updates'],identical_initial_samples=same,augmented_conditional_examples=applied,all_null_targets_unchanged=True,baseline_manifest_sha256=sha(basepath),candidate_manifest_sha256=sha(path))
