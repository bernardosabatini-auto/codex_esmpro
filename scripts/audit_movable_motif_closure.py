"""CPU provenance, saved-parameter replay and NumPy rescoring of paired outputs."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from latentfold.movable_motif_closure import replay
from profile_movable_motif_closure import score
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha
from profile_gpu import atomic_json


def audit(report):
    root=Path(__file__).resolve().parents[1]
    d=json.loads(report.read_text())
    run=Path(d['run'])
    if (d['status']!='complete' or len(d['records'])!=64 or len(d['controls'])!=16
            or sha(run/'manifest.json')!=d['manifest_sha256']
            or sha(run/'predictions.h5')!=d['predictions_sha256']):
        raise ValueError('Incomplete or changed profile')
    for file,digest in d['sources'].items():
        if sha(Path(file))!=digest or sha(run/'source_snapshot'/Path(file).name)!=digest:
            raise ValueError('Changed scientific source')
    baseline=Path(d['baseline_report'])
    if sha(baseline)!=d['baseline_report_sha256']:
        raise ValueError('Changed original parent report')
    old=json.loads(baseline.read_text())
    original=Path(old['run'])/'predictions.h5'
    if sha(original)!=d['baseline_predictions_sha256']:
        raise ValueError('Changed original backbones')
    spec=old['spec']
    previous=json.loads((root/spec['source_report']).read_text())
    manifest=Path(previous['manifest_path'])
    if sha(root/spec['source_report'])!=spec['source_report_sha256'] or sha(manifest)!=previous['manifest_sha256']:
        raise ValueError('Changed original fragment provenance')
    training=json.loads(manifest.read_text())
    c=training['config']
    fragments=[r for r in c['sources'] if r['path']==c['fragments']]
    if len(fragments)!=1 or sha(Path(c['fragments']))!=fragments[0]['sha256']:
        raise ValueError('Changed original isolated-fragment archive')
    items=load_conditions(training['config']['fragments'],[r['id'] for r in d['selected']],'c20_center',cohort='train')
    expected={(p,a,r['id'],s) for p in ('fixed_pose','free_pose') for a in ('generated_cond','native_cond')
              for r in d['selected'] for s in range(4)}
    keys=[(r['pose_arm'],r['arm'],r['target_id'],r['generation_slot']) for r in d['records']]
    if len(set(keys))!=64 or set(keys)!=expected:
        raise ValueError('Missing, duplicated or substituted cases')
    maximum=0.
    with h5py.File(original,'r',locking=False) as original_file,h5py.File(run/'predictions.h5','r',locking=False) as f:
        for r in d['records']:
            key=r['arm']+'/'+r['target_id']+'/'+str(r['generation_slot'])
            g=f[r['pose_arm']+'/'+key]
            parent,source,result=g['parent'][:],g['source'][:],g['backbone'][:]
            for name,value in [('parent',parent),('source',source)]:
                if not np.array_equal(value,original_file[key+'/'+name][:]):
                    raise ValueError('Changed original input')
            item=dict(items[r['target_id']],id=r['target_id'],arm=r['arm'])
            saved=r['solver']
            reconstructed=replay(source,parent,item['start'],20,spec,saved['torsion_offsets'],saved['pose'],
                                 free_pose=r['pose_arm']=='free_pose')
            error=float(np.max(np.abs(reconstructed-result)))
            maximum=max(error,maximum)
            if error!=0:
                raise ValueError('Saved parameter replay differs')
            rescored=score(result,source,parent,item,r['generation_slot'],r['bucket'],spec,r['pose_arm'])
            if rescored!={k:v for k,v in r.items() if k!='solver'}:
                raise ValueError('Independent NumPy rescore differs')
    for c in d['controls']:
        if not c['noop_exact'] or c['noop_calls'] or not c['repeat_exact'] or c['pose_max_abs']>.005:
            raise ValueError('Numerical control failed')
    counts={(p,a):sum(r['steric_eligible'] for r in d['records'] if r['pose_arm']==p and r['arm']==a)
            for p in ('fixed_pose','free_pose') for a in ('generated_cond','native_cond')}
    qualified=(counts['free_pose','generated_cond']>=12
               and counts['free_pose','generated_cond']>counts['fixed_pose','generated_cond']
               and counts['free_pose','native_cond']==16)
    if qualified!=d['qualified']:
        raise ValueError('Qualification decision differs')
    return dict(status='complete',records=64,controls=16,replay_max_abs=maximum,
        provenance_passed=True,rescore_passed=True,qualified=qualified,
        profile_report_sha256=sha(report),profile_manifest_sha256=d['manifest_sha256'],
        predictions_sha256=d['predictions_sha256'])


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    d=audit(a.profile)
    atomic_json(a.report.with_suffix('.json'),d)
    a.report.with_suffix('.md').write_text('# Movable-motif profile audit\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')
    print(json.dumps(d,indent=2))


if __name__=='__main__':main()
