"""Bound inputs for full decoder adaptation, preserving the original codec."""
import json
from pathlib import Path
import h5py
from fragment_decoder_training_core import (load_training, training_batch, panel, initial_adapter,
    expected_frozen_state, canonical_frozen_state, refold_eligibility)
from prepare_overfit import sha


def initial_model_state(c):
    result={}
    for k,v in expected_frozen_state(c).items():
        name,separator,rest=k.partition('.')
        wrapped=name+'.base.'+rest if separator and name in ('cond_factory','pair_repr_builder') else k
        result['decoder.'+wrapped]=v
    result.update({'adapter.'+k:v for k,v in initial_adapter(c).items()})
    return result


def audit(c):
    from fragment_decoder_training_core import audit as audit_closed
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']: raise ValueError('Changed denoising source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text())
    closed=json.loads(Path(c['closed_manifest']).read_text()); old=closed['config']; audit_closed(old)
    report=json.loads(Path(c['closed_report']).read_text())
    if (spec!=c['spec'] or closed['status']!='complete' or report['status']!='complete'
            or not report['fragment_decoder'] or report['profile_only'] or not report['numerically_qualified']
            or report['qualified'] or report['manifest_sha256']!=sha(c['closed_manifest'])
            or Path(c['closed_manifest']).parent.name!=spec['closed_decoder_run']
            or any(c[k]!=old[k] for k in ('selected','training_ids','baseline_manifest','baseline_report','baseline_predictions',
                                         'fragments','decoder_checkpoint','diagnostic_manifest','diagnostic_predictions'))
            or c['updates']!=spec['profile_updates' if c['profile_only'] else 'updates']):
        raise ValueError('Changed full-decoder experiment lineage')
    with h5py.File(c['fragments']) as f:
        if sorted(f['train'])!=c['training_ids'] or len(c['training_ids'])!=512: raise ValueError('Changed training inventory')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if (p['status']!='complete' or not p['profile_only'] or not p['qualified'] or not p.get('fragment_decoder_fm')
                or p['protocol_sha256']!=sha(c['protocol']) or c['allocation_minutes']!=p['recommended_full_minutes']
                or c['allocation_minutes']>150): raise ValueError('Unqualified denoising profile')
    return spec
