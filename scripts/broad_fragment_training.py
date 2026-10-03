"""Explicitly audited breadth by objective continuation; older recipes are unchanged."""
import json
from pathlib import Path

from prepare_overfit import sha


PATH_OVERRIDES = ('extension_protocol', 'broad_corpus_protocol', 'warm_protocol',
                  'warm_parent_manifest', 'warm_parent_report', 'warm_predictions',
                  'checkpoint', 'data_manifest', 'data_report', 'fragments',
                  'expanded_protocol', 'latent_weight_protocol', 'profile_report', 'factorial_profile_report')
OVERRIDES = {'extension_arm', 'profile_only', 'seed', 'updates', 'evaluation_steps',
             'total_prior_updates', 'work_cap_seconds', 'allocation_minutes',
             'training_protein_count', 'motif_mass', 'corpus', 'latent_weight_profile_audit', 'freeze_trunk'}
OVERRIDES |= set(PATH_OVERRIDES) | {k + '_sha256' for k in PATH_OVERRIDES}
OVERRIDES |= {'condition_selection','condition_selection_sha256'}


def audit_broad(c):
    for key in PATH_OVERRIDES:
        if key in ('profile_report', 'factorial_profile_report') and c['profile_only']:
            continue
        if sha(c[key]) != c[key + '_sha256']:
            raise ValueError('Changed broad training source ' + key)
    spec = json.loads(Path(c['broad_corpus_protocol']).read_text())
    root = Path(c['broad_corpus_protocol']).parent.parent
    if not spec['broad_short_corpus'] or c['extension_arm'] not in spec['arms']:
        raise ValueError('Undeclared broader training arm')
    arm = spec['arms'][c['extension_arm']]
    if bool(c.get('condition_selection'))!=bool(spec.get('condition_quality_study')):
        raise ValueError('Changed condition-selection policy')
    if c.get('condition_selection'):
        from fragment_quality_training import selection_for_config
        selection_for_config(c)
    if type(c.get('freeze_trunk', False)) is not bool or c.get('freeze_trunk', False) != arm.get('freeze_trunk', False):
        raise ValueError('Changed generator freeze policy')
    if c.get('freeze_trunk'):
        if not spec.get('freeze_trunk_study') or not c.get('warm_start'):
            raise ValueError('Unbound learned-generator freezing')
        evidence = root / spec['source_calibration_report']
        if sha(evidence) != spec['source_calibration_sha256']:
            raise ValueError('Changed source-designability prerequisite')
        calibration = json.loads(evidence.read_text())
        if calibration['status'] != 'complete':
            raise ValueError('Incomplete source-designability prerequisite')
        for source_arm in ('original512', 'added7429'):
            rows = [r for r in calibration['summary'] if r['arm'] == source_arm]
            if sum(r['proteins'] for r in rows) != 64 or sum(r['designable'] for r in rows) < 48:
                raise ValueError('Insufficient source designability for freeze study')
    for key in ('extension_protocol', 'warm_protocol', 'latent_weight_protocol'):
        if c[key] != c['broad_corpus_protocol']:
            raise ValueError('Inconsistent broader training protocol')
    parent = Path(c['warm_parent_manifest'])
    m = json.loads(parent.read_text())
    report = json.loads(Path(c['warm_parent_report']).read_text())
    pc = m['config']
    if (parent.parent.name != spec['parent'] or m['status'] != 'complete' or m['updates'] != 2000
            or report['status'] != 'complete' or report['manifest_sha256'] != sha(parent)
            or report['total_training_updates'] != spec['total_prior_updates']):
        raise ValueError('Wrong or unaudited broader training parent')
    for key in set(pc) | set(c):
        if key not in OVERRIDES and (key not in pc or key not in c or c[key] != pc[key]):
            raise ValueError('Changed inherited setting ' + key)
    if (c['corpus'] != arm['corpus'] or c.get('motif_mass') != arm['motif_mass']
            or c['latent_motif_weight'] != spec['weight'] or c['seed'] != spec['seed']
            or c['total_prior_updates'] != spec['total_prior_updates']
            or c['sampling_control_mode'] != spec['sampling_control_mode']):
        raise ValueError('Changed corpus/objective/schedule')
    if c['expanded_protocol'] != str((root / spec['assembly_protocol']).resolve()):
        raise ValueError('Wrong corpus construction protocol')
    dm = json.loads(Path(c['data_manifest']).read_text())
    dr = json.loads(Path(c['data_report']).read_text())
    n = dm['training_protein_count']
    if (dm['status'] != 'complete' or dr['status'] != 'complete' or not dm['training_gate_passed']
            or not dr['training_gate_passed'] or dr['manifest_sha256'] != c['data_manifest_sha256']
            or dm['fragments_sha256'] != c['fragments_sha256'] or dr['fragments_sha256'] != c['fragments_sha256']
            or c['training_protein_count'] != n or dr['training_protein_count'] != n
            or dm['corpus'] != arm['corpus'] or dm['conditions_per_training_protein'] != 12
            or dm['original_proteins_preserved'] != 512 or dm['development_proteins_preserved'] != 16
            or dm['config']['base_fragments_sha256'] != pc['fragments_sha256']
            or dm['config']['protocol_sha256'] != c['expanded_protocol_sha256']):
        raise ValueError('Unqualified assembled training data')
    if (arm['corpus'] == 'control512' and n != 512) or (arm['corpus'] == 'broad' and not 7424 <= n <= 8192):
        raise ValueError('Changed training breadth')
    ids = [r['id'] for r in dm['config']['training_targets']]
    if len(ids) != n or len(set(ids)) != n or not set(c['evaluation_train_ids']) <= set(ids):
        raise ValueError('Changed training inventory or capacity panel')
    if len(dm['config']['shards']) != 4:
        raise ValueError('All four data shards required')
    partitions = []
    for source in dm['config']['shards']:
        for key in ('manifest', 'report', 'fragments'):
            if sha(source[key]) != source[key + '_sha256']:
                raise ValueError('Changed assembled data provenance')
        d = json.loads(Path(source['report']).read_text())
        if d['status'] != 'complete' or not d['data_gate_passed'] or d['manifest_sha256'] != source['manifest_sha256'] or d['fragments_sha256'] != source['fragments_sha256']:
            raise ValueError('Unqualified assembly shard')
        partitions.append(d['partition'])
    if set(partitions) != set(range(4)):
        raise ValueError('Missing or repeated data partition')
    if (c['checkpoint'] != str(parent.parent / 'ema_2000.ckpt')
            or c['warm_predictions'] != str(parent.parent / 'evaluation_2000.h5')
            or c['updates'] != (40 if c['profile_only'] else spec['updates'])
            or c['evaluation_steps'] != ([40] if c['profile_only'] else spec['evaluation_steps'])):
        raise ValueError('Changed continuation state or update schedule')
    if not c['profile_only']:
        matched = json.loads(Path(c['factorial_profile_report']).read_text())
        if (matched['status'] != 'complete' or not matched['profile_only']
                or matched['matched_training_updates'] != 40
                or matched['protocol_sha256'] != c['broad_corpus_protocol_sha256']
                or set(matched['initial_predictions']) != set(spec['arms'])
                or any(n != 32 for n in matched['initial_predictions'].values())
                or c['profile_report_sha256'] not in {s['report_sha256'] for s in matched['sources']}):
            raise ValueError('Unqualified matched factorial profile')
        profile = json.loads(Path(c['profile_report']).read_text())
        if not profile['profile_qualified']:
            raise ValueError('Unqualified broad training profile')
        for key in ('checkpoint_sha256', 'fragments_sha256', 'extension_protocol_sha256',
                    'extension_arm', 'seed', 'motif_mass', 'corpus'):
            if profile['config'][key] != c[key]:
                raise ValueError('Wrong matched profile')
        if profile['config'].get('freeze_trunk', False) != c.get('freeze_trunk', False):
            raise ValueError('Wrong generator-freezing profile')
    return dict(spec, training_protein_count=n)
