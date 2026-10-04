"""Bound training inputs and matched-draw checks for the qualified anchor pilot."""
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from prepare_overfit import sha


def tensor_hash(x):return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def state_hash(state):
    h=hashlib.sha256()
    for key,value in sorted(state.items()):h.update(key.encode());h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def audit(c):
    if c.get('repaint_student_training'):
        from repaint_student_training_core import audit as audit_repaint
        return audit_repaint(c)
    if c.get('positive_coverage_training'):
        from native_positive_training_core import audit as audit_positive
        return audit_positive(c)
    for source in c['sources']:
        if sha(source['path'])!=source['sha256']:raise ValueError('Changed native-training source: '+source['path'])
    spec=json.loads(Path(c['protocol']).read_text());labels=json.loads(Path(c['labels_manifest']).read_text())
    if spec!=c['spec'] or labels['status']!='complete' or labels['spec']!=spec or c['arm'] not in spec['arms']:
        raise ValueError('Changed training protocol or label source')
    for source in labels['sources']:
        if sha(source['path'])!=source['sha256']:raise ValueError('Changed qualified label provenance')
    qualification=json.loads(Path(labels['comparison']).read_text())
    wanted=sorted(r['target_id'] for r in qualification['preferences'] if r['confirmed'])
    if not qualification['gate']['qualified'] or c['training_ids']!=wanted or c['training_ids']!=sorted(r['target_id'] for r in labels['rows']):
        raise ValueError('Training labels lack prospective qualification')
    if c['control_ids']!=labels['control_ids'] or c['checkpoint']!=labels['checkpoint'] or c['decoder_checkpoint']!=labels['decoder_checkpoint'] or c['fragments']!=labels['fragments']:
        raise ValueError('Changed parent or inference inputs')
    if c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates']) or sha(labels['pairs'])!=labels['pairs_sha256']:
        raise ValueError('Changed schedule or label arrays')
    gm=json.loads(Path(labels['generation_manifest']).read_text())
    if (Path(gm['config']['model_manifest']).parent.name!=spec['parent']
            or c['initial_predictions']!=str(Path(labels['generation_manifest']).parent/'predictions.h5')
            or c['sampling_seed']!=gm['config']['spec']['seed']):raise ValueError('Changed sampler initialization')
    if not c['profile_only']:
        profile=json.loads(Path(c['profile_comparison']).read_text())
        if profile['status']!='complete' or not profile['qualified'] or not profile['profile_only'] or profile['matched_updates']!=spec['profile_updates'] or profile['protocol_sha256']!=sha(c['protocol']):raise ValueError('Unqualified training profile')
    return spec,labels


def load_pairs(c,*,audited=None):
    if c.get('repaint_student_training'):
        from repaint_student_training_core import load_pairs as load_repaint
        return load_repaint(c,audited=audited)
    if c.get('positive_coverage_training'):
        from native_positive_training_core import load_positives
        return load_positives(c)
    spec,labels=audit(c);data={}
    gm=json.loads(Path(labels['generation_manifest']).read_text());gc=gm['config']
    with h5py.File(labels['pairs']) as f,h5py.File(c['fragments']) as fr,h5py.File(c['initial_predictions']) as gen:
        if set(f)!=set(c['training_ids']):raise ValueError('Changed training pair inventory')
        for row in labels['rows']:
            ident=row['target_id'];g=f[ident];source=fr['train/'+ident];q=source['conditions/c20_center'];n=row['length'];start=int(q.attrs['start'])
            if (not np.array_equal(g['positive'][:],source['reference_z'][:])
                    or not np.array_equal(g['negative'][:],gen['new/'+ident+'/latent'][row['negative_slot']])
                    or not np.array_equal(g['fragment_latent'][:],q['latent'][:])
                    or not np.array_equal(g['fragment'][:],q['fragment'][:])
                    or g.attrs['sequence']!=q.attrs['sequence'] or int(g.attrs['start'])!=start or int(g.attrs['length'])!=n):
                raise ValueError('Latent label or isolated input changed')
            features,keep=fragment_features(torch.from_numpy(g['fragment_latent'][:]),str(g.attrs['sequence']),length=n,start=start)
            data[ident]=dict(length=n,bucket=row['bucket'],positive=torch.from_numpy(g['positive'][:]),negative=torch.from_numpy(g['negative'][:]),
                             features=features,keep=keep,coordinates=fragment_coordinates(torch.from_numpy(g['fragment'][:]),length=n,start=start))
    return data
