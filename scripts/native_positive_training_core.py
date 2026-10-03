"""Positive-only coverage expansion, bound to both qualification cohorts."""
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from prepare_overfit import sha

NUMERIC_KEYS=('parent','seed','updates','profile_updates','beta','adapter_lr','gradient_clip','optimizer','warmup_updates','lr_schedule','batches','adapter_ema_decay')
INPUT_KEYS=('control_ids','checkpoint','decoder_checkpoint','fragments','initial_predictions','sampling_seed')
DRAW_KEYS=('step','length','batch','learning_rate_factor','noise_sha256','time_sha256','rng_sha256','self_conditioned')


def qualified_inventory(old,new):
    if old['status']!='complete' or new['status']!='complete' or not new['gate']['qualified']:
        raise ValueError('Unqualified reference labels')
    old_ids={r['target_id'] for r in old['rows']};all_new={r['target_id'] for r in new['rows']}
    if len(old_ids)!=10 or len(all_new)!=64 or old_ids&all_new:raise ValueError('Changed or overlapping source cohorts')
    rows=[dict(target_id=r['target_id'],length=r['length'],bucket=r['bucket'],origin='original') for r in old['rows']]
    rows += [dict(target_id=r['target_id'],length=r['length'],bucket=r['bucket'],origin='new') for r in new['rows'] if r['qualified']]
    return sorted(rows,key=lambda r:r['target_id'])


def check_draws(a,b):
    if len(a)!=len(b) or any(x[k]!=y[k] for x,y in zip(a,b) for k in DRAW_KEYS):
        raise ValueError('Changed noise, time, history or schedule')


def audit(c):
    from native_anchor_training_core import audit as old_audit
    for source in c['sources']:
        if sha(source['path'])!=source['sha256']:raise ValueError('Changed positive-training source: '+source['path'])
    spec=json.loads(Path(c['protocol']).read_text());labels=json.loads(Path(c['labels_manifest']).read_text())
    if spec!=c['spec'] or c['arm']!='positive_coverage' or spec['arms']!={'positive_coverage':{'negative_weight':0.0}} or labels['status']!='complete':raise ValueError('Changed positive-only protocol')
    for source in labels['sources']:
        if sha(source['path'])!=source['sha256']:raise ValueError('Changed positive-label provenance')
    old=json.loads(Path(labels['original_labels']).read_text());new=json.loads(Path(labels['qualification']).read_text())
    old_run=json.loads(Path(labels['matched_control']).read_text());oc=old_run['config'];os,_=old_audit(oc)
    coverage=json.loads(Path(labels['coverage_protocol']).read_text())
    if new['protocol_sha256']!=sha(labels['coverage_protocol']) or coverage['matched_positive_control']!=Path(labels['matched_control']).parent.name:raise ValueError('Unbound coverage qualification')
    if (old_run['status']!='complete' or oc['arm']!='positive' or oc['profile_only']
            or oc['labels_manifest']!=labels['original_labels'] or any(spec[k]!=os[k] for k in NUMERIC_KEYS)):
        raise ValueError('Changed matched positive recipe')
    rows=qualified_inventory(old,new)
    if labels['rows']!=rows or c['training_ids']!=[r['target_id'] for r in rows]:raise ValueError('Missing or ranked qualified positives')
    if any(c[k]!=oc[k] for k in INPUT_KEYS):raise ValueError('Changed parent or historical controls')
    if c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates']):raise ValueError('Changed endpoint')
    if sha(labels['positives'])!=labels['positives_sha256']:raise ValueError('Changed positive arrays')
    if not c['profile_only']:
        profile=json.loads(Path(c['profile_comparison']).read_text())
        if (profile['status']!='complete' or not profile['qualified'] or not profile['profile_only']
                or profile['matched_updates']!=spec['profile_updates'] or profile['protocol_sha256']!=sha(c['protocol'])
                or profile['labels_manifest_sha256']!=sha(c['labels_manifest'])):raise ValueError('Unqualified positive coverage profile')
    return spec,labels


def load_positives(c):
    _,labels=audit(c);data={}
    with h5py.File(labels['positives']) as f,h5py.File(c['fragments']) as fr:
        if set(f)!=set(c['training_ids']):raise ValueError('Changed positive inventory')
        for row in labels['rows']:
            ident=row['target_id'];g=f[ident];source=fr['train/'+ident];q=source['conditions/c20_center'];n=row['length'];start=int(q.attrs['start'])
            if (set(g)!={'positive','fragment_latent','fragment'} or n!=len(source['reference_z'])
                    or row['bucket']!=((n+127)//128)*128
                    or not np.array_equal(g['positive'][:],source['reference_z'][:])
                    or not np.array_equal(g['fragment_latent'][:],q['latent'][:])
                    or not np.array_equal(g['fragment'][:],q['fragment'][:])
                    or g.attrs['sequence']!=q.attrs['sequence'] or int(g.attrs['start'])!=start or int(g.attrs['length'])!=n):raise ValueError('Changed positive endpoint or isolated input')
            features,keep=fragment_features(torch.from_numpy(g['fragment_latent'][:]),str(g.attrs['sequence']),length=n,start=start)
            data[ident]=dict(length=n,bucket=row['bucket'],positive=torch.from_numpy(g['positive'][:]),features=features,keep=keep,
                             coordinates=fragment_coordinates(torch.from_numpy(g['fragment'][:]),length=n,start=start))
    return data
