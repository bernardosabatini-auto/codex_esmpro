"""Provenance and independent scoring of reference-positive coverage expansion."""
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha


def audit_generation(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed positive-coverage input')
    selection=json.loads(Path(c['selection']).read_text());spec=json.loads(Path(c['protocol']).read_text())
    if (selection['status']!='selected' or c['spec']!=spec or selection['spec']!=spec
            or c['target_ids']!=selection['target_ids'] or c['selected']!=selection['selected']
            or c['fragments']!=selection['fragments'] or not c.get('native_positive_coverage')
            or (spec['native_samples'],spec['decoder_steps'],spec['native_batch_size'])!=(2,3,2)):
        raise ValueError('Changed selected positive-coverage recipe')
    for r in selection['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed selection provenance')
    excluded=set(selection['excluded']);expected=[]
    with h5py.File(c['fragments']) as f:
        if len(f['train'])!=512:raise ValueError('Wrong training corpus')
        for bucket in (128,256,384,512):
            pool=[i for i in f['train'] if i not in excluded and (int(f['train/'+i].attrs['length'])+127)//128*128==bucket]
            pool.sort(key=lambda i:hashlib.sha256(f"{spec['selection_seed']}:{i}".encode()).hexdigest())
            for k,ident in enumerate(pool[:spec['per_length_bucket'][str(bucket)]]):
                g=f['train/'+ident];q=g['conditions/c20_center']
                expected.append(dict(id=ident,family=str(g.attrs['family']),length=int(g.attrs['length']),bucket=bucket,partition=k%4,start=int(q.attrs['start']),sequence=str(q.attrs['sequence'])))
        if expected!=c['selected'] or len(expected)!=64 or set(c['target_ids'])&set(f['development']):raise ValueError('Changed disjoint selection')
    pm=json.loads(Path(c['profile_manifest']).read_text());pd=json.loads(Path(c['profile_report']).read_text());pc=pm['config']
    if (Path(c['profile_manifest']).parent.name!='extra_fragment_validation_50194966'
            or pm['status']!='complete' or pd['status']!='complete' or not pd['native_generation_gate']
            or pd['manifest_sha256']!=sha(c['profile_manifest']) or pd['predictions_sha256']!=sha(c['profile_predictions'])
            or len(pm['native_controls'])!=16 or any(r['peak_reserved_GiB']>75 for r in pm['native_controls'])
            or c['decoder_checkpoint']!=pc['decoder_checkpoint'] or c['fragments']!=pc['fragments']
            or next(r['sha256'] for r in pc['sources'] if r['path']==c['decoder_checkpoint'])!=sha(c['decoder_checkpoint'])
            or c['historical_seed']!=pc['spec']['native_seed'] or c['allocation_minutes']!=10 or c['work_cap_seconds']!=480):
        raise ValueError('Unqualified inherited two-sample decoder profile')
    controls=[min(r['id'] for r in pc['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    if c['control_ids']!=controls or set(controls)&set(c['target_ids']):raise ValueError('Changed historical controls')
    return spec


def analyze_generation(run):
    from extra_fragment_validation_core import load_conditions
    from native_anchor_calibration import score_native_decodes
    from latentfold.metrics import ca_metrics
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),native_generation_gate=False)
    c=m['config'];spec=audit_generation(c);items=load_conditions(c['fragments'],c['target_ids'],'c20_center',cohort='train')
    if m['predictions_sha256']!=sha(run/'predictions.h5') or m['training_updates_executed']!=0:raise ValueError('Changed decoder outputs')
    score=score_native_decodes(run,m,items,expected_count=64,minimum_both=spec['generation_gate']['minimum_both_raw_and_roundtrip'],minimum_long=spec['generation_gate']['minimum_long_both_raw_and_roundtrip'])
    if len(m['historical_controls'])!=4 or {r['target_id'] for r in m['historical_controls']}!=set(c['control_ids']):raise ValueError('Missing historical controls')
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['profile_predictions']) as old:
        if set(f)!={'native','historical'} or set(f['historical'])!=set(c['control_ids']):raise ValueError('Changed stored inventory')
        for ident in c['control_ids']:
            a,b=f['historical/'+ident],old['native/'+ident]
            if not np.array_equal(a['latent'][:],b['latent'][:]):raise ValueError('Historical latent changed')
            metrics=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(a['backbone'][:],b['backbone'][:])]
            r=dict(target_id=ident,max_ca_rmsd=max(x['ca_rmsd'] for x in metrics),min_ca_lddt=min(x['ca_lddt'] for x in metrics))
            if r not in m['historical_controls'] or r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99:raise ValueError('Historical decoder output changed')
    return dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],protocol_sha256=sha(c['protocol']),historical_controls=4,**score,
                elapsed_seconds=m['elapsed_seconds'],scope='64fresh training references, two independently seeded decodes each. Raw/roundtrip qualification only; designability and same-refold retention remain unmeasured.')
