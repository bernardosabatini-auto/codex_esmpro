"""Only supervised endpoints differ between the matched isolated-input arms."""
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from teacher_coordinates_profile_core import sha

INPUT_KEYS=('control_ids','checkpoint','decoder_checkpoint','fragments','initial_predictions','sampling_seed')
DRAW_KEYS=('step','length','batch','ids','learning_rate_factor','noise_sha256','time_sha256','rng_sha256','self_conditioned')


def check_draws(a,b):
    if len(a)!=len(b) or any(x[k]!=y[k] for x,y in zip(a,b) for k in DRAW_KEYS):
        raise ValueError('Unmatched protein/slot, noise, time, history or schedule')


def audit(c):
    if c.get('repaint_student_training') is not True or c.get('positive_coverage_training'):
        raise ValueError('Explicit, exclusive RePaint student lineage required')
    verified={}
    def verify(source):
        path=source['path']
        if path not in verified:verified[path]=sha(path)
        if verified[path]!=source['sha256']:raise ValueError('Changed training provenance: '+path)
    for source in c['sources']:verify(source)
    if any(c[k] not in verified for k in ('protocol','labels_manifest','checkpoint','decoder_checkpoint','fragments','initial_predictions','baseline_manifest','baseline_report')):
        raise ValueError('Unbound training input')
    spec=json.loads(Path(c['protocol']).read_text());labels=json.loads(Path(c['labels_manifest']).read_text())
    if (spec!=c['spec'] or labels['spec']!=spec or labels['status']!='complete'
            or spec['arms']!=['native_matched','repaint_positive'] or c['arm'] not in spec['arms']):
        raise ValueError('Changed endpoint pilot protocol')
    for source in labels['sources']:verify(source)
    for key in ('checkpoint','decoder_checkpoint','fragments','parent_manifest','generation_manifest','teacher_predictions'):
        if labels[key] not in verified:raise ValueError('Unbound label source')
    for key in ('checkpoint','decoder_checkpoint','fragments'):
        if c[key]!=labels[key]:raise ValueError('Changed parent or isolated input')
    if (Path(labels['parent_manifest']).parent.name!=spec['parent'] or Path(c['checkpoint']).name!=spec['checkpoint']
            or sha(labels['labels'])!=labels['labels_sha256']):raise ValueError('Changed endpoint arrays or parent')
    from compare_fragment_repaint_teacher import teacher_gate
    from compare_native_anchor_models import verify_outcome
    # Snapshot protocols resolve relative evidence through their runs symlink;
    # the bound evidence path itself is authoritative, not the snapshot reports.
    qualified=[s['path'] for s in labels['sources'] if Path(s['path']).name==Path(spec['qualification']).name]
    if len(qualified)!=1:raise ValueError('Unbound teacher comparison')
    comparison=json.loads(Path(qualified[0]).read_text())
    total=next(r for r in comparison['summary'] if r['arm']=='oracle_repaint' and r['bucket'] is None)
    if comparison['status']!='complete' or not teacher_gate(total):raise ValueError('Unqualified teacher')
    selected=[]
    for source in comparison['source_reports']:
        if sha(source['path'])!=source['sha256']:raise ValueError('Changed teacher or reused parent outcomes')
        d=json.loads(Path(source['path']).read_text())
        for r in d['records']:
            if r['arm']=='oracle_repaint':
                verify_outcome(r)
                if r['scaffold_joint_success']:selected.append(r)
    selected.sort(key=lambda r:(r['target_id'],r['generation_slot']))
    if len(selected)!=13 or len({r['family'] for r in selected})!=9 or labels['qualification_records']!=selected:
        raise ValueError('Dropped, added or changed qualified completions')
    wanted=[dict(label_id=f'label_{i:02d}',target_id=r['target_id'],family=r['family'],bucket=r['bucket'],length=r['length'],generation_slot=r['generation_slot'],strict_refold_indices=r['scaffold_successful_refold_indices']) for i,r in enumerate(selected)]
    if labels['rows']!=wanted or c['training_ids']!=[r['label_id'] for r in wanted]:raise ValueError('Changed label multiplicity')
    bm=json.loads(Path(c['baseline_manifest']).read_text());bd=json.loads(Path(c['baseline_report']).read_text());bc=bm['config']
    controls=[next(r['id'] for r in bc['selected'] if r['bucket']==bucket) for bucket in (128,256,384,512)]
    if (bm['status']!='complete' or bd['status']!='complete' or bd['manifest_sha256']!=verified[c['baseline_manifest']]
            or bd['predictions_sha256']!=verified[c['initial_predictions']] or bc['arm']!='parent6000'
            or c['initial_predictions']!=str(Path(c['baseline_manifest']).parent/'predictions.h5')
            or c['checkpoint']!=bc['checkpoint'] or c['fragments']!=bc['fragments']
            or c['decoder_checkpoint']!=bc['decoder_checkpoint'] or c['control_ids']!=controls
            or c['sampling_seed']!=bc['spec']['seed']):raise ValueError('Changed initial parent prediction controls')
    if c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates']):raise ValueError('Changed update budget')
    if not c['profile_only']:
        if c['profile_comparison'] not in verified:raise ValueError('Unbound paired profile')
        profile=json.loads(Path(c['profile_comparison']).read_text())
        if (profile['status']!='complete' or not profile['qualified'] or not profile['profile_only']
                or profile['matched_updates']!=40 or profile['protocol_sha256']!=sha(c['protocol'])
                or profile['labels_manifest_sha256']!=sha(c['labels_manifest'])
                or c['allocation_minutes']!=profile['recommended_full_minutes']):raise ValueError('Unqualified matched profiles')
    return spec,labels


def load_pairs(c,*,audited=None):
    spec,labels=audit(c) if audited is None else audited
    data={}
    with h5py.File(labels['labels']) as f,h5py.File(c['fragments']) as fr,h5py.File(labels['teacher_predictions']) as gen:
        if set(f)!=set(c['training_ids']):raise ValueError('Wrong label inventory')
        for row in labels['rows']:
            key=row['label_id'];ident=row['target_id'];g=f[key];source=fr['train/'+ident];q=source['conditions/'+spec['condition']];n=row['length'];start=int(q.attrs['start'])
            if (set(g)!={'native_matched','repaint_positive','fragment_latent','fragment'} or n!=len(source['reference_z'])
                    or row['bucket']!=((n+127)//128)*128
                    or not np.array_equal(g['native_matched'][:],source['reference_z'][:])
                    or not np.array_equal(g['repaint_positive'][:],gen['new/'+ident+'/latent'][row['generation_slot']])
                    or not np.array_equal(g['fragment_latent'][:],q['latent'][:])
                    or not np.array_equal(g['fragment'][:],q['fragment'][:])
                    or str(g.attrs['sequence'])!=str(q.attrs['sequence']) or int(g.attrs['start'])!=start
                    or int(g.attrs['length'])!=n or str(g.attrs['target_id'])!=ident):raise ValueError('Changed latent target or isolated student input')
            features,keep=fragment_features(torch.from_numpy(g['fragment_latent'][:]),str(g.attrs['sequence']),length=n,start=start)
            data[key]=dict(length=n,bucket=row['bucket'],target_id=ident,positive=torch.from_numpy(g[c['arm']][:]),
                           features=features,keep=keep,coordinates=fragment_coordinates(torch.from_numpy(g['fragment'][:]),length=n,start=start))
    return data
