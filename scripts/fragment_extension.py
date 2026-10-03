"""Strict lineage for one additional matched conditional-training interval."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit_extension(c):
    path=Path(c['extension_protocol'])
    if sha(path)!=c['extension_protocol_sha256']:raise ValueError('Changed extension protocol')
    spec=json.loads(path.read_text());arm=c['extension_arm'];parent=Path(c['warm_parent_manifest'])
    if arm not in spec['parents'] or parent.parent.name!=spec['parents'][arm] or c['warm_protocol']!=c['extension_protocol'] or c['warm_protocol_sha256']!=c['extension_protocol_sha256']:raise ValueError('Wrong extension parent')
    m=json.loads(parent.read_text());report=json.loads(Path(c['warm_parent_report']).read_text());pc=m['config']
    if m['status']!='complete' or m['updates']!=2000 or report['status']!='complete' or report['manifest_sha256']!=sha(parent) or report['total_training_updates']!=4000:raise ValueError('Unaudited extension parent')
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
