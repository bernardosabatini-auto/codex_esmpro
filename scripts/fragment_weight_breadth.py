"""Bind the weighted512 experiment to its existing unweighted control."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit(c):
    for key in ('weight_breadth_protocol', 'weight_breadth_baseline'):
        if sha(c[key]) != c[key+'_sha256']:
            raise ValueError('Changed weighted breadth provenance')
    spec = json.loads(Path(c['weight_breadth_protocol']).read_text())
    path = Path(c['weight_breadth_baseline'])
    base = json.loads(path.read_text())
    if (path.parent.name != spec['baseline'] or base['status'] != 'complete'
            or base['updates'] != spec['updates'] or base['config'].get('latent_motif_weight')
            or c.get('training_protein_count') != spec['training_protein_count']
            or c.get('latent_motif_weight') != spec['weight']
            or spec['weight'] != 3 or spec['training_protein_count'] != 512
            or c.get('extension_protocol')):
        raise ValueError('Invalid weighted breadth contrast')
    operational = {'profile_only', 'updates', 'evaluation_steps', 'work_cap_seconds',
                   'allocation_minutes', 'profile_report', 'profile_report_sha256'}
    for key, value in base['config'].items():
        if key not in operational and c.get(key) != value:
            raise ValueError('Changed weighted breadth recipe: '+key)
    if c['updates'] != (40 if c['profile_only'] else spec['updates']) or c['evaluation_steps'] != ([40] if c['profile_only'] else [500, 2000]):
        raise ValueError('Changed weighted breadth exposure')
    if any(c.get(k) for k in ('rollout_motif', 'auxiliary_motif', 'target_frame_training', 'backbone_tokens', 'fragment_representation', 'sampling_control_mode')):
        raise ValueError('Additional undeclared contrast')
    return spec
