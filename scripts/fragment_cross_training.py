"""Qualification of a matched dynamic fragment-routing experiment."""
import json
from pathlib import Path

from prepare_overfit import sha


def audit_cross_config(c, spec):
    architecture = c['fragment_cross_attention']
    if (not spec.get('fragment_cross_study') or not c.get('freeze_trunk')
            or not c.get('warm_start') or c['corpus'] != 'control512'
            or set(architecture) != {'cross_width', 'cross_heads', 'cross_route'}
            or architecture['cross_width'] != 128 or architecture['cross_heads'] != 4
            or architecture['cross_route'] not in ('all', 'motif')
            or c['extension_arm'] != architecture['cross_route']
            or c.get('condition_selection') or c.get('motif_mass') is not None
            or any(c.get(k) for k in ('auxiliary_motif', 'rollout_motif', 'backbone_tokens',
                                      'fragment_representation', 'target_frame_training'))):
        raise ValueError('Undeclared cross-attention contrast')
    root = Path(c['broad_corpus_protocol']).parent.parent
    for source in spec['prerequisite_reports']:
        path = root / source['path']
        if sha(path) != source['sha256'] or json.loads(path.read_text())['status'] != 'complete':
            raise ValueError('Changed cross-attention prerequisite')


def audit_cross_manifest(m):
    names = m.get('frozen_adapter_names', [])
    if (not names or any(n.startswith('cross_') for n in names)
            or not m.get('cross_initial') or not m.get('frozen_adapter_initial')
            or m['frozen_adapter_initial'] != m.get('frozen_adapter_final')
            or not m.get('frozen_adapter_ema_exact') or not m.get('frozen_generator_ema_exact')):
        raise ValueError('Parent adapter/generator freeze failed')


def compare_cross_traces(manifests):
    if set(manifests) != {'all', 'motif'}:
        raise ValueError('Both routing arms required')
    a, b = manifests['all'], manifests['motif']
    for m in (a, b):
        audit_cross_manifest(m)
    for key in ('cross_initial', 'frozen_adapter_initial', 'frozen_initial', 'trainable_parameters'):
        if a[key] != b[key]:
            raise ValueError('Unmatched cross-attention initialization or capacity')
    fields = ('step', 'length', 'batch', 'ids', 'conditions', 'learning_rate_factor',
              'self_conditioned', 'noise_sha256', 'time_sha256', 'drop_sha256',
              'rng_sha256', 'global_rng_sha256')
    if len(a['training']) != len(b['training']):
        raise ValueError('Unequal training exposure')
    for x, y in zip(a['training'], b['training']):
        if any(x[k] != y[k] for k in fields):
            raise ValueError('Unmatched training draw')
    return len(a['training'])
