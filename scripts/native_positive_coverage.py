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


def audit_refold(c):
    from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
    for key in ('generation_manifest','generation_report','generated_predictions','predictions','protocol','teacher_profile_manifest','teacher_profile_report','teacher_probe'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed native-positive refold input: '+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];spec=audit_generation(gc);d=json.loads(Path(c['generation_report']).read_text())
    if (gm['status']!='complete' or d['status']!='complete' or not d['native_generation_gate']
            or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256']
            or d['historical_controls']!=4 or d['native_controls']!=64 or len(d['native_records'])!=128
            or c['protocol']!=gc['protocol']):raise ValueError('Unaudited or failed native generation')
    pm=json.loads(Path(c['teacher_profile_manifest']).read_text());pd=json.loads(Path(c['teacher_profile_report']).read_text());probe=json.loads(Path(c['teacher_probe']).read_text())
    if (Path(c['teacher_profile_manifest']).parent.name!=spec['refold_profile'] or pm['status']!='complete' or pd['status']!='complete'
            or pd['manifest_sha256']!=c['teacher_profile_manifest_sha256'] or pd['refolded_sha256']!=sha(Path(c['teacher_profile_manifest']).parent/'refolded.h5')
            or len(pm['records'])!=256 or not pm['teacher_deterministic_algorithms'] or max(r['peak_reserved_bytes'] for r in pm['records'])>75*2**30
            or any(c[k]!=pm['config'][k] for k in TEACHER_KEYS) or not probe['deterministic_algorithms'] or probe['status']!='complete'
            or probe['failed_pairs'] or probe['feature_mutations'] or probe['feature_rng_changes'] or not probe['fresh_feature_hashes_match']
            or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in probe['original_comparisons'])):raise ValueError('Unqualified inherited teacher execution')
    if (c['assay']!='fragment_preference_refold' or not c['native_positive_coverage'] or c['teacher_deterministic_algorithms'] is not True
            or c.get('mpnn_mode','ca')!='ca' or c['num_sequences']!=8 or c['expected_backbones']!=32 or len(c['entries'])!=32
            or c['partition'] not in range(4) or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010):raise ValueError('Changed positive qualification budget')
    selected=[r for r in gc['selected'] if r['partition']==c['partition']];wanted=[]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['generated_predictions']) as gen,h5py.File(c['predictions']) as out:
        for row in selected:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            for slot in range(2):wanted.append(make_entry(row,q,slot,len(wanted),arm='native_latent'))
        if c['entries']!=wanted or set(out)!={'motifs'}|{r['name'] for r in wanted} or set(out['motifs'])!={r['id'] for r in selected}:raise ValueError('Dropped or changed reference candidate')
        for r in wanted:
            if (not np.array_equal(out[r['dataset']][:],gen['native/'+r['target_id']+'/backbone'][r['generation_slot']][None])
                    or not np.array_equal(out['motifs/'+r['target_id']][:],fr['train/'+r['target_id']+'/conditions/c20_center/fragment'][:])):raise ValueError('Changed reference or motif coordinates')
    return gc,spec


def qualify_sources(records,generation_rows,selected,limits):
    """Both decodes must independently pass; never pool their sequence attempts."""
    from compare_native_anchor_models import verify_outcome
    expected={(r['id'],slot) for r in selected for slot in range(2)}
    if (len(records)!=len(expected) or {(r['target_id'],r['generation_slot']) for r in records}!=expected
            or len(generation_rows)!=len(expected) or {(r['target_id'],r['generation_slot']) for r in generation_rows}!=expected):raise ValueError('Incomplete reference qualification inventory')
    raw={(r['target_id'],r['generation_slot']):r for r in generation_rows};per_source=[]
    for r in records:
        if len(r['refolds'])!=8:raise ValueError('Changed per-decode design budget')
        verify_outcome(r)
    for source in selected:
        rows=sorted([r for r in records if r['target_id']==source['id']],key=lambda r:r['generation_slot'])
        qualifies=all(r['scaffold_joint_success'] and raw[source['id'],r['generation_slot']]['raw_gate_passed']
                      and raw[source['id'],r['generation_slot']]['full_native_ca_rmsd']<=1 for r in rows)
        per_source.append(dict(target_id=source['id'],length=source['length'],bucket=source['bucket'],qualified=qualifies,
                               successful_refold_indices=[r['scaffold_successful_refold_indices'] for r in rows]))
    good=[r for r in per_source if r['qualified']];long=sum(r['length']>256 for r in good);buckets=len({r['bucket'] for r in good})
    checks=dict(coverage=len(good)>=limits['minimum_new_qualified'],buckets=buckets>=limits['minimum_buckets'],long=long>=limits['minimum_new_long_qualified'])
    return dict(qualified=all(checks.values()),checks=checks,new_qualified=len(good),new_long_qualified=long,buckets=buckets),per_source
