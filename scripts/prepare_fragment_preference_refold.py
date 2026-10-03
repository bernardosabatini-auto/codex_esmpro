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


def make_entry(row, q, slot, index):
    name=f"preference_{row['partition']}_{index:03d}"
    return dict(name=name,dataset=name,head='parent6000',arm='parent6000',target_id=row['id'],
                family=row['family'],length=row['length'],bucket=row['bucket'],slot=0,
                generation_slot=slot,fixed_start=int(q.attrs['start']),motif_start=int(q.attrs['start']),
                fixed_sequence=str(q.attrs['sequence']),repeatability_control=index==0)


def audit_inputs(c):
    for key in ('generation_manifest','generation_report','generated_predictions','predictions',
                'protocol','teacher_profile_manifest','teacher_profile_report','teacher_probe'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed preference input: '+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];spec=audit_generation(gc)
    d=json.loads(Path(c['generation_report']).read_text())
    if (gm['status']!='complete' or d['status']!='complete' or d['controls']!=68
            or d['manifest_sha256']!=c['generation_manifest_sha256']
            or d['predictions_sha256']!=c['generated_predictions_sha256']
            or gm['predictions_sha256']!=c['generated_predictions_sha256']
            or len(d['records'])!=128 or c['protocol']!=gc['protocol']):
        raise ValueError('Unaudited generation')
    profile=json.loads(Path(c['teacher_profile_manifest']).read_text())
    pd=json.loads(Path(c['teacher_profile_report']).read_text())
    probe=json.loads(Path(c['teacher_probe']).read_text())
    if (Path(c['teacher_profile_manifest']).parent.name!=spec['refold_profile']
            or profile['status']!='complete' or pd['status']!='complete'
            or pd['manifest_sha256']!=c['teacher_profile_manifest_sha256']
            or not profile['teacher_deterministic_algorithms']
            or len(profile['records'])!=240
            or max(r['peak_reserved_bytes'] for r in profile['records'])>75*2**30
            or probe['status']!='complete' or not probe['deterministic_algorithms']
            or probe['failed_pairs'] or probe['feature_mutations'] or probe['feature_rng_changes']
            or not probe['fresh_feature_hashes_match']
            or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in probe['original_comparisons'])):
        raise ValueError('Unqualified inherited refolding execution')
    if (any(c[k]!=profile['config'][k] for k in TEACHER_KEYS)
            or c.get('teacher_deterministic_algorithms') is not True
            or c['assay']!='fragment_preference_refold' or c.get('mpnn_mode','ca')!='ca'
            or c['expected_backbones']!=32 or len(c['entries'])!=32 or c['partition'] not in range(4)
            or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010):
        raise ValueError('Changed refolding recipe or inventory')
    rows=[r for r in gc['selected'] if r['partition']==c['partition']]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['predictions']) as out,h5py.File(c['generated_predictions']) as gen:
        wanted=[]
        for row in rows:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            for slot in range(4):wanted.append(make_entry(row,q,slot,len(wanted)))
        if c['entries']!=wanted or set(out)!={'motifs'}|{r['dataset'] for r in wanted} or set(out['motifs'])!={r['id'] for r in rows}:
            raise ValueError('Dropped, added, or changed candidate')
        for r in wanted:
            q=fr['train/'+r['target_id']+'/conditions/c20_center']
            if (not np.array_equal(out[r['dataset']][:],gen['new/'+r['target_id']+'/backbone'][r['generation_slot']][None])
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
    gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];spec=audit_generation(gc)
    profile=root/'runs'/spec['refold_profile'];prior=json.loads((profile/'manifest.json').read_text())['config']
    for partition in range(4):
        path=Path(str(a.output_prefix)+f'_{partition}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:prior[k] for k in TEACHER_KEYS}
        c.update(assay='fragment_preference_refold',partition=partition,expected_backbones=32,entries=[],
                 allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True)
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
                    entry=make_entry(row,q,slot,len(c['entries']));c['entries'].append(entry)
                    out.create_dataset(entry['dataset'],data=gen['new/'+row['id']+'/backbone'][slot][None])
        c.update(predictions=str(inputs),predictions_sha256=sha(inputs));audit_inputs(c)
        with path.open('x') as f:json.dump(c,f,indent=2)
        print(partition,len(c['entries']),flush=True)


if __name__=='__main__':main()
