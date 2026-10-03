"""Bound pretrained local-flow experiment; prior failures remain closed."""
import json,hashlib
from pathlib import Path
import h5py,torch
from latentfold.pretrained_masked_flow import ScaffoldContext
from prepare_overfit import sha
from native_anchor_training_core import state_hash
from fragment_preference_calibration import audit_generation


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed pretrained-mask source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());base=json.loads(Path(c['baseline_manifest']).read_text());bc=base['config'];audit_generation(bc)
    failed=json.loads(Path(c['failed_small_report']).read_text());fm=json.loads(Path(c['failed_small_manifest']).read_text());report=json.loads(Path(c['baseline_report']).read_text())
    if (spec!=c['spec'] or not spec['pretrained_masked'] or base['status']!='complete' or report['status']!='complete' or report['controls']!=68
        or report['manifest_sha256']!=sha(c['baseline_manifest']) or report['predictions_sha256']!=sha(c['baseline_predictions'])
        or c['checkpoint']!=bc['checkpoint'] or Path(c['checkpoint']).parent.name!=spec['parent']
        or c['selected']!=bc['selected'] or c['fragments']!=bc['fragments'] or c['decoder_checkpoint']!=bc['decoder_checkpoint']
        or failed['status']!='complete' or failed['profile_only'] or failed['refold_gate']['qualified']
        or failed['manifest_sha256']!=sha(c['failed_small_manifest']) or Path(c['failed_small_manifest']).parent.name!=spec['failed_small_run']
        or c['training_ids']!=fm['config']['training_ids'] or c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates'])):raise ValueError('Changed pretrained local-flow lineage')
    dm=json.loads(Path(c['diagnostic_manifest']).read_text())
    if dm['status']!='complete' or dm['predictions_sha256']!=sha(c['diagnostic_predictions']) or dm['config']['baseline_predictions']!=c['baseline_predictions']:raise ValueError('Changed native parity source')
    with h5py.File(c['fragments']) as f:
        if sorted(f['train'])!=c['training_ids'] or len(c['training_ids'])!=512:raise ValueError('Changed training cohort')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if p['status']!='complete' or not p['profile_only'] or not p['qualified'] or not p['pretrained_masked'] or p['protocol_sha256']!=sha(c['protocol']) or c['allocation_minutes']!=p['recommended_full_minutes']:raise ValueError('Unqualified pretrained masked profile')
    return spec


def initial_state(c):
    parent=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True)
    state={'net.'+k.replace('_orig_mod.',''):v for k,v in parent['ema'].items()};state.update({'fragment.'+k:v for k,v in parent['fragment_adapter'].items()})
    state.update({'context.'+k:v for k,v in ScaffoldContext(parent['arch']['d_model'],c['spec']['seed']).state_dict().items()})
    if any(v.dtype!=torch.float32 for v in state.values()):raise ValueError('Unexpected nonFP32 parent state')
    return state
