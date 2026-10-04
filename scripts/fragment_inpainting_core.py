"""Bound training-only data and controls for conditional coordinate inpainting."""
import json
from pathlib import Path
import h5py
import torch
from fragment_decoder_training_core import (load_training as base_load_training, training_batch,
    panel, canonical_frozen_state, expected_frozen_state, initial_adapter)
from fragment_decoder_fm_core import initial_model_state
from latentfold.fragment_inpainting import place_fragment
from prepare_overfit import sha


def audit(c):
    for r in c['sources']:
        if sha(r['path']) != r['sha256']:raise ValueError('Changed inpainting source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text())
    closed=json.loads(Path(c['closed_manifest']).read_text());old=closed['config']
    report=json.loads(Path(c['closed_report']).read_text())
    student=json.loads(Path(c['student_comparison']).read_text())
    baseline=json.loads(Path(c['baseline_manifest']).read_text())
    if (spec!=c['spec'] or c['updates']!=spec['profile_updates' if c['profile_only'] else 'updates']
            or closed['status']!='complete' or report['status']!='complete'
            or not report['numerically_qualified'] or report['qualified'] or report['profile_only']
            or report['manifest_sha256']!=sha(c['closed_manifest'])
            or Path(c['closed_manifest']).parent.name!=spec['closed_decoder']
            or student['status']!='complete' or student['development_screen_qualified']!={'repaint_positive':False}
            or Path(c['baseline_manifest']).parent.name!=spec['baseline_generation']
            or baseline['status']!='complete'
            or any(c[k]!=old[k] for k in ('selected','training_ids','baseline_manifest','baseline_report','baseline_predictions',
                                         'fragments','decoder_checkpoint','diagnostic_manifest','diagnostic_predictions'))):
        raise ValueError('Unbound inpainting prerequisites or data')
    for key in ('baseline','diagnostic'):
        m=json.loads(Path(c[key+'_manifest']).read_text())
        if m['status']!='complete':raise ValueError('Incomplete original control')
    with h5py.File(c['fragments']) as f:
        if len(c['training_ids'])!=512 or sorted(f['train'])!=c['training_ids']:raise ValueError('Changed training inventory')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if (p['status']!='complete' or not p['profile_only'] or not p['qualified']
                or not p.get('fragment_inpainting') or p['protocol_sha256']!=sha(c['protocol'])
                or c['allocation_minutes']!=p['recommended_full_minutes'] or c['allocation_minutes']>150):
            raise ValueError('Unqualified conditional-state profile')
    if 'junction_protocol' in c:
        from fragment_junction_core import audit_sources
        audit_sources(c)
    elif any(k.startswith('junction_') for k in c):
        raise ValueError('Junction settings require a bound prospective protocol')
    if 'flank_protocol' in c:
        from fragment_flank_core import audit_sources
        audit_sources(c)
    elif any(k.startswith('flank_') or k == 'context_flank' for k in c):
        raise ValueError('Context flank requires a bound prospective protocol')
    return spec


def load_training(c):
    data=base_load_training(c)
    # Known target atoms must encode exactly the supplied fragment geometry,
    # within the FP32 rounding of its separately saved rigid pose.
    with h5py.File(c['fragments']) as f:
        for ident,row in data.items():
            target=row['backbone'];centered=target-target.mean((0,1),keepdim=True)
            for name in c['spec']['conditions']:
                q=f['train/'+ident+'/conditions/'+name];start=int(q.attrs['start'])
                placed=place_fragment(torch.from_numpy(q['fragment'][:]),target[None],start)[0]
                keep=row['conditions'][name]['keep']
                error=float((placed[keep]-centered[keep]).abs().max())
                if error>1e-4:raise ValueError('Supervised motif differs from isolated input')
    return data


def refold_eligibility(summary, records, ids, spec):
    arms={'parent','native_direct','generated_cond','generated_null','native_cond','native_null','generated_untrained','native_untrained'}
    index={r['arm']:r for r in summary}
    if (len(ids)!=32 or len(set(ids))!=32 or set(index)!=arms or len(summary)!=8
            or len(records)!=1024 or {(r['arm'],r['target_id'],r['generation_slot']) for r in records}!=
               {(a,i,k) for a in arms for i in ids for k in range(4)}):raise ValueError('Incomplete inpainting inventory')
    for arm in arms:
        rows=[r for r in records if r['arm']==arm]
        if (index[arm]['samples']!=128 or index[arm]['raw']!=sum(r['raw_gate_passed'] for r in rows)
                or index[arm]['valid']!=sum(r['coarse_valid'] for r in rows)):raise ValueError('Outcome totals disagree')
    if (index['parent']['raw'],index['parent']['valid'],index['native_direct']['raw'],index['native_direct']['valid'])!=(25,128,128,128):
        raise ValueError('Historical control changed')
    checks=dict(strict_success_possible=index['generated_cond']['raw']>=spec['refold_eligibility']['generated_cond_min_raw'],
                designability_floor_possible=index['generated_cond']['valid']>=spec['refold_eligibility']['generated_cond_min_valid'])
    return dict(qualified=all(checks.values()),checks=checks)
