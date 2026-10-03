"""Bound whole-chain clock experiment; previous fixed-scaffold recipe remains closed."""
import json,hashlib
from pathlib import Path
import h5py,torch
from latentfold.scaffold_clock_flow import ClockAdapter
from prepare_overfit import sha
from native_anchor_training_core import state_hash
from fragment_preference_calibration import audit_generation


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed scaffold-clock source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());base=json.loads(Path(c['baseline_manifest']).read_text());bc=base['config'];audit_generation(bc)
    failed=json.loads(Path(c['failed_small_report']).read_text());fm=json.loads(Path(c['failed_small_manifest']).read_text());report=json.loads(Path(c['baseline_report']).read_text())
    if (spec!=c['spec'] or spec.get('scaffold_start')!=.5 or base['status']!='complete' or report['status']!='complete' or report['controls']!=68
        or report['manifest_sha256']!=sha(c['baseline_manifest']) or report['predictions_sha256']!=sha(c['baseline_predictions'])
        or c['checkpoint']!=bc['checkpoint'] or Path(c['checkpoint']).parent.name!=spec['parent']
        or c['selected']!=bc['selected'] or c['fragments']!=bc['fragments'] or c['decoder_checkpoint']!=bc['decoder_checkpoint']
        or failed['status']!='complete' or failed['profile_only'] or failed['refold_gate']['qualified']
        or failed['manifest_sha256']!=sha(c['failed_small_manifest']) or Path(c['failed_small_manifest']).parent.name!=spec['failed_small_run']
        or c['training_ids']!=fm['config']['training_ids'] or c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates'])):raise ValueError('Changed scaffold-clock lineage')
    dm=json.loads(Path(c['diagnostic_manifest']).read_text())
    if dm['status']!='complete' or dm['predictions_sha256']!=sha(c['diagnostic_predictions']) or dm['config']['baseline_predictions']!=c['baseline_predictions']:raise ValueError('Changed native parity source')
    with h5py.File(c['fragments']) as f:
        if sorted(f['train'])!=c['training_ids'] or len(c['training_ids'])!=512:raise ValueError('Changed training cohort')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if p['status']!='complete' or not p['profile_only'] or not p['qualified'] or not p['scaffold_clock'] or p['protocol_sha256']!=sha(c['protocol']) or c['allocation_minutes']!=p['recommended_full_minutes']:raise ValueError('Unqualified pretrained masked profile')
    closed=json.loads(Path(c['closed_fixed_report']).read_text())
    if closed['status']!='complete' or closed['profile_only'] or closed['refold_gate']['qualified'] or Path(closed['manifest_path']).parent.name!=spec['closed_fixed_run']:
        raise ValueError('Expected the completed failed fixed-scaffold experiment')
    return spec


def initial_state(c):
    parent=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True)
    state={'net.'+k.replace('_orig_mod.',''):v for k,v in parent['ema'].items()};state.update({'fragment.'+k:v for k,v in parent['fragment_adapter'].items()})
    state.update({'clock.'+k:v for k,v in ClockAdapter(parent['arch']['d_model'],c['spec']['seed']).state_dict().items()})
    if any(v.dtype!=torch.float32 for v in state.values()):raise ValueError('Unexpected nonFP32 parent state')
    return state


def quality_gate(summary, records, ids, spec):
    lookup={r['arm']:r for r in summary}
    expected={'parent','native_direct','generated_cond','generated_null','native_cond','native_null','initial_generated_cond'}
    if set(lookup)!=expected or len(summary)!=7 or len(ids)!=32 or len(set(ids))!=32 or any(r['samples']!=128 for r in summary):
        raise ValueError('Full seven-arm 128-output inventory required')
    if lookup['parent']['raw']!=25 or lookup['parent']['valid']!=128 or lookup['native_direct']['raw']!=128:
        raise ValueError('Historical control changed')
    observed={(r['arm'],r['target_id'],r['generation_slot']) for r in records}
    if len(records)!=896 or observed!={(a,i,k) for a in expected for i in ids for k in range(4)}:
        raise ValueError('Incomplete or duplicated quality rows')
    for arm in expected:
        rr=[r for r in records if r['arm']==arm]
        if lookup[arm]['raw']!=sum(r['raw_gate_passed'] for r in rr) or lookup[arm]['valid']!=sum(r['coarse_valid'] for r in rr):
            raise ValueError('Quality summaries disagree with rows')
    improved=sum(sum(r['raw_gate_passed'] for r in records if r['target_id']==i and r['arm']=='generated_cond')>sum(r['raw_gate_passed'] for r in records if r['target_id']==i and r['arm']=='parent') for i in ids)
    gate=spec['full_gate'];g=lookup['generated_cond'];n=lookup['native_cond']
    checks=dict(native_capacity=n['raw']>=gate['native_cond_min_raw'],native_validity=n['valid']>=gate['native_cond_min_valid'],
        generated_validity=g['valid']>=gate['generated_cond_min_valid'],raw_gain_over_parent=g['raw']>=gate['generated_cond_min_raw'],
        raw_gain_over_null=g['raw']>lookup['generated_null']['raw'],raw_gain_over_initial=g['raw']>lookup['initial_generated_cond']['raw'],
        families=improved>=gate['minimum_improved_families'])
    return dict(qualified=all(checks.values()),checks=checks,improved_families=improved)
