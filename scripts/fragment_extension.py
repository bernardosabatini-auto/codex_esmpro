"""Strict lineage for one additional matched conditional-training interval."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit_extension(c):
    path=Path(c['extension_protocol'])
    if sha(path)!=c['extension_protocol_sha256']:raise ValueError('Changed extension protocol')
    spec=json.loads(path.read_text());arm=c['extension_arm'];parent=Path(c['warm_parent_manifest'])
    if arm not in spec['parents'] or parent.parent.name!=spec['parents'][arm] or c['warm_protocol']!=c['extension_protocol'] or c['warm_protocol_sha256']!=c['extension_protocol_sha256']:raise ValueError('Wrong extension parent')
    if spec.get('sampling_control_mode'):
        root=path.parent.parent
        failed=root/'runs'/spec['failed_profile']/'manifest.json'
        if sha(root/spec['original_protocol'])!=spec['original_protocol_sha256'] or sha(failed)!=spec['failed_profile_manifest_sha256']:raise ValueError('Changed original batch failure')
        failure=json.loads(failed.read_text())
        if failure['status']!='failed' or failure['updates']!=0 or failure['error']!='ValueError: Initial sampler/batch control failed' or spec['evaluation_batch_size']!=4:raise ValueError('Wrong original batch failure')
    if c.get('sampling_control_mode')!=spec.get('sampling_control_mode'):raise ValueError('Changed batch control scope')
    m=json.loads(parent.read_text());report=json.loads(Path(c['warm_parent_report']).read_text());pc=m['config']
    if m['status']!='complete' or m['updates']!=2000 or report['status']!='complete' or report['manifest_sha256']!=sha(parent) or report['total_training_updates']!=spec['total_prior_updates']:raise ValueError('Unaudited extension parent')
    if spec.get('training_protein_count') and (c.get('training_protein_count')!=spec['training_protein_count'] or c.get('training_protein_count')!=pc.get('training_protein_count')):raise ValueError('Changed declared training breadth')
    if spec.get('data_protocol'):
        for key in ('extension_data_manifest','extension_data_report','extension_data_targets'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed breadth augmentation prerequisite')
        dm=json.loads(Path(c['extension_data_manifest']).read_text());dd=json.loads(Path(c['extension_data_report']).read_text())
        if dm['status']!='complete' or dd['status']!='complete' or not dd['training_gate_passed'] or dd['manifest_sha256']!=c['extension_data_manifest_sha256'] or dm['targets_sha256']!=c['extension_data_targets_sha256'] or dm['config']['protocol_sha256']!=sha(path.parent.parent/spec['data_protocol']) or dm['config']['fragments_sha256']!=c['fragments_sha256']:raise ValueError('Unqualified breadth augmentation prerequisite')
    keys=('fragments_sha256','batches','evaluation_train_ids','initial_predictions_sha256','decoder_checkpoint_sha256','distance_precision','geometry_protocol_sha256')
    if any(c[k]!=pc[k] for k in keys) or c['total_prior_updates']!=spec['total_prior_updates'] or c['seed']!=spec['seed']:raise ValueError('Changed extension data or exposure')
    if c.get('latent_motif_weight',1.)!=(3. if arm=='weighted' else 1.) or c.get('latent_motif_weight',1.)!=pc.get('latent_motif_weight',1.):raise ValueError('Changed extension objective')
    if c['checkpoint']!=str(parent.parent/'ema_2000.ckpt') or c['warm_predictions']!=str(parent.parent/'evaluation_2000.h5'):raise ValueError('Wrong continuation state')
    if c['updates']!=(40 if c['profile_only'] else spec['updates']) or c['evaluation_steps']!=([40] if c['profile_only'] else spec['evaluation_steps']):raise ValueError('Changed extension schedule')
    if any(c.get(k) for k in ('auxiliary_motif','rollout_motif','target_frame_training','backbone_tokens','fragment_representation')):raise ValueError('Undeclared extension contrast')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if not p['profile_qualified'] or p['config']['extension_arm']!=arm or any(p['config'][k]!=c[k] for k in ('checkpoint_sha256','fragments_sha256','extension_protocol_sha256','seed')):raise ValueError('Wrong extension profile')
    return spec


def validate_capacity_panel(c,parent_config,training_ids):
    expected=parent_config["evaluation_train_ids"] if c.get("extension_protocol") else sorted(training_ids)
    if c["evaluation_train_ids"]!=expected:raise ValueError("Changed capacity panel")
