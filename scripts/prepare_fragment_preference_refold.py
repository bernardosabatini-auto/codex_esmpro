"""Refold every prospective training candidate with an unchanged eight-design budget."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from fragment_preference_calibration import audit_generation
from prepare_overfit import sha

TEACHER_KEYS=('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies',
              'teacher_artifacts','precision','usalign','usalign_sha256')


def make_entry(row, q, slot, index, arm='parent6000'):
    name=f"preference_{row['partition']}_{index:03d}"
    return dict(name=name,dataset=name,head=arm,arm=arm,target_id=row['id'],
                family=row['family'],length=row['length'],bucket=row['bucket'],slot=0,
                generation_slot=slot,fixed_start=int(q.attrs['start']),motif_start=int(q.attrs['start']),
                fixed_sequence=str(q.attrs['sequence']),repeatability_control=index==0)


def audit_inputs(c, *, audited_generation=None):
    if c.get('trajectory_guidance_refold'):
        from trajectory_guidance_refolding import audit_refold
        return audit_refold(c)
    if c.get('retrieved_context_refold'):
        from retrieved_context_refolding import audit_refold
        return audit_refold(c,audited_generation=audited_generation)
    if c.get('movable_motif_refold'):
        from movable_motif_refolding import audit_refold
        return audit_refold(c,audited_generation=audited_generation)
    if c.get('torsion_closure_refold'):
        from torsion_closure_refolding import audit_refold
        return audit_refold(c,audited_generation=audited_generation)
    if c.get('oracle_teacher_refold'):
        from fragment_repaint_teacher_refolding import audit_refold
        return audit_refold(c,audited_generation=audited_generation)
    if c.get('pretrained_masked_refold') or c.get('scaffold_clock_refold') or c.get('fragment_decoder_refold') or c.get('fragment_decoder_fm_refold') or c.get('fragment_inpainting_refold'):
        from pretrained_masked_refolding import audit_refold
        return audit_refold(c,audited_generation=audited_generation)
    if c.get('native_positive_coverage'):
        from native_positive_coverage import audit_refold
        return audit_refold(c)
    for key in ('generation_manifest','generation_report','generated_predictions','predictions',
                'protocol','teacher_profile_manifest','teacher_profile_report','teacher_probe'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed preference input: '+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config']
    if audited_generation is None:spec=audit_generation(gc)
    else:
        old_gc,spec=audited_generation
        if gc!=old_gc or gc['spec']!=spec:raise ValueError('Changed previously audited generation')
    d=json.loads(Path(c['generation_report']).read_text());native=bool(spec.get('native_anchor_calibration'));count=16 if native else 32
    if spec.get('repaint_student_model_validation'):
        from repaint_student_model_validation import require_refold_eligibility
        require_refold_eligibility(d)
    if (gm['status']!='complete' or d['status']!='complete' or d['controls']!=4+2*count
            or d['manifest_sha256']!=c['generation_manifest_sha256']
            or d['predictions_sha256']!=c['generated_predictions_sha256']
            or gm['predictions_sha256']!=c['generated_predictions_sha256']
            or len(d['records'])!=4*count or c['protocol']!=gc['protocol']):
        raise ValueError('Unaudited generation')
    if native and (not d['native_generation_gate'] or len(d['native_records'])!=32 or d['native_controls']!=16):raise ValueError('Native decoder generation gate failed')
    profile=json.loads(Path(c['teacher_profile_manifest']).read_text())
    pd=json.loads(Path(c['teacher_profile_report']).read_text())
    probe=json.loads(Path(c['teacher_probe']).read_text())
    if (Path(c['teacher_profile_manifest']).parent.name!=spec['refold_profile']
            or profile['status']!='complete' or pd['status']!='complete'
            or pd['manifest_sha256']!=c['teacher_profile_manifest_sha256']
            or not profile['teacher_deterministic_algorithms']
            or len(profile['records'])!=(256 if native else 240)
            or max(r['peak_reserved_bytes'] for r in profile['records'])>75*2**30
            or probe['status']!='complete' or not probe['deterministic_algorithms']
            or probe['failed_pairs'] or probe['feature_mutations'] or probe['feature_rng_changes']
            or not probe['fresh_feature_hashes_match']
            or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in probe['original_comparisons'])):
        raise ValueError('Unqualified inherited refolding execution')
    if (any(c[k]!=profile['config'][k] for k in TEACHER_KEYS)
            or c.get('teacher_deterministic_algorithms') is not True
            or c['assay']!='fragment_preference_refold' or c.get('mpnn_mode','ca')!='ca'
            or c['expected_backbones']!=(24 if native else 32) or len(c['entries'])!=c['expected_backbones'] or c['partition'] not in range(4)
            or c['allocation_minutes']!=(30 if native else 35) or c['work_cap_seconds']!=(1710 if native else 2010)):
        raise ValueError('Changed refolding recipe or inventory')
    rows=[r for r in gc['selected'] if r['partition']==c['partition']]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['predictions']) as out,h5py.File(c['generated_predictions']) as gen:
        wanted=[]
        for row in rows:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            for slot in range(4):wanted.append(make_entry(row,q,slot,len(wanted),arm=gc['arm']))
            if native:
                for slot in range(2):wanted.append(make_entry(row,q,slot,len(wanted),arm='native_latent'))
        if c['entries']!=wanted or set(out)!={'motifs'}|{r['dataset'] for r in wanted} or set(out['motifs'])!={r['id'] for r in rows}:
            raise ValueError('Dropped, added, or changed candidate')
        for r in wanted:
            q=fr['train/'+r['target_id']+'/conditions/c20_center']
            if (not np.array_equal(out[r['dataset']][:],gen[('native/' if r['arm']=='native_latent' else 'new/')+r['target_id']+'/backbone'][r['generation_slot']][None])
                    or not np.array_equal(out['motifs/'+r['target_id']][:],q['fragment'][:])):
                raise ValueError('Changed generated or supplied coordinates')
    # Reused native budgets use identical teacher weights, MPNN and precision.
    for source in gc['native_sources']:
        nc=json.loads(Path(source['manifest']).read_text())['config']
        for k in TEACHER_KEYS:
            if k!='seed' and nc[k]!=c[k]:raise ValueError('Native teacher recipe differs: '+k)
    return gc,spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True)
    p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.generation.resolve()
    gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];spec=audit_generation(gc);native=bool(spec.get('native_anchor_calibration'))
    if spec.get('repaint_student_model_validation'):
        from repaint_student_model_validation import require_refold_eligibility
        require_refold_eligibility(json.loads((root/'reports'/(run.name+'.json')).read_text()))
    profile=root/'runs'/spec['refold_profile'];prior=json.loads((profile/'manifest.json').read_text())['config']
    for partition in range(4):
        path=Path(str(a.output_prefix)+f'_{partition}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:prior[k] for k in TEACHER_KEYS}
        c.update(assay='fragment_preference_refold',partition=partition,expected_backbones=24 if native else 32,entries=[],
                 allocation_minutes=30 if native else 35,work_cap_seconds=1710 if native else 2010,teacher_deterministic_algorithms=True)
        for key,value in [('generation_manifest',run/'manifest.json'),('generation_report',root/'reports'/(run.name+'.json')),
                          ('generated_predictions',run/'predictions.h5'),('protocol',gc['protocol']),
                          ('teacher_profile_manifest',profile/'manifest.json'),('teacher_profile_report',root/'reports'/(profile.name+'.json')),
                          ('teacher_probe',root/spec['teacher_execution_evidence'])]:
            c[key]=str(value);c[key+'_sha256']=sha(value)
        with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(inputs,'x') as out:
            for row in (r for r in gc['selected'] if r['partition']==partition):
                q=fr['train/'+row['id']+'/conditions/c20_center']
                out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
                for slot in range(4):
                    entry=make_entry(row,q,slot,len(c['entries']),arm=gc['arm']);c['entries'].append(entry)
                    out.create_dataset(entry['dataset'],data=gen['new/'+row['id']+'/backbone'][slot][None])
                if native:
                    for slot in range(2):
                        entry=make_entry(row,q,slot,len(c['entries']),arm='native_latent');c['entries'].append(entry)
                        out.create_dataset(entry['dataset'],data=gen['native/'+row['id']+'/backbone'][slot][None])
        c.update(predictions=str(inputs),predictions_sha256=sha(inputs));audit_inputs(c,audited_generation=(gc,spec))
        with path.open('x') as f:json.dump(c,f,indent=2)
        print(partition,len(c['entries']),flush=True)


if __name__=='__main__':main()
