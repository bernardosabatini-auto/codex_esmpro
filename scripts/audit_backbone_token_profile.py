"""Qualify direct atom inputs with matched initialization, draws and predictions."""
import json
from pathlib import Path

import h5py
import numpy as np

from prepare_overfit import sha


def audit_matched_profile(root, report, baseline_id, adapter_key='adapter_initial'):
    root, report = Path(root), Path(report)
    d = json.loads(report.read_text())
    # The report binds the exact source manifest; resolve through its run name.
    manifest = root / 'runs' / report.stem / 'manifest.json'
    new = json.loads(manifest.read_text())
    baseline_path = root / f'runs/fragment_training_{baseline_id}/manifest.json'
    base = json.loads(baseline_path.read_text())
    if d['manifest_sha256'] != sha(manifest) or not d['profile_qualified'] or new['status'] != 'complete' or new['updates'] != 40:
        raise ValueError('Incomplete/unaudited backbone profile')
    if new[adapter_key] != base['adapter_initial'] or new['frozen_initial'] != base['frozen_initial']:
        raise ValueError('Changed shared initialization')
    for key in ('seed', 'batches', 'checkpoint_sha256', 'fragments_sha256', 'decoder_checkpoint_sha256'):
        if new['config'][key] != base['config'][key]:
            raise ValueError('Changed profile recipe')
    trace = ('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned',
             'noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    if len(new['training']) != 40 or len(base['training']) != 40:
        raise ValueError('Missing profile steps')
    for x, y in zip(base['training'], new['training']):
        if any(x[k] != y[k] for k in trace):
            raise ValueError('Changed profile random trace')
    matched = 0
    with h5py.File(baseline_path.parent / 'evaluation_0.h5') as left, h5py.File(manifest.parent / 'evaluation_0.h5') as right:
        for mode in ('conditioned', 'null'):
            if set(left['development/' + mode]) != set(right['development/' + mode]):
                raise ValueError('Changed profile case inventory')
            for ident in left['development/' + mode]:
                for key in ('latent', 'backbone'):
                    path = f'development/{mode}/{ident}/{key}'
                    if not np.array_equal(left[path][:], right[path][:]):
                        raise ValueError('Changed initial profile output')
                matched += 4
    if matched != 32:
        raise ValueError('Missing initial profile samples')
    return dict(matched_steps=40, identical_initial_samples=matched,
                baseline_manifest_sha256=sha(baseline_path), candidate_manifest_sha256=sha(manifest))


def audit(root, report):
    d=json.loads(Path(report).read_text())
    if not d['config'].get('backbone_tokens'):raise ValueError('Not a backbone-token profile')
    return audit_matched_profile(root,report,'49928663','shared_adapter_initial')
