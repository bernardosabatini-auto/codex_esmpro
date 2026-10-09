"""Full paired CPU mechanism assay using the unchanged qualified profile solver."""
import argparse
import json
import time
from pathlib import Path
import h5py
import numpy as np
from latentfold.movable_motif_closure import close_movable_motif, replay
from profile_movable_motif_closure import score
from audit_movable_motif_closure import audit as audit_profile
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha
from profile_gpu import atomic_json


POSES=('fixed_pose','free_pose')
CONTEXTS=('generated_cond','native_cond')


def inputs(root, protocol):
    spec=json.loads(protocol.read_text())
    profile_path=root/spec['profile_report']
    if sha(profile_path)!=spec['profile_report_sha256']:
        raise ValueError('Changed qualified profile')
    profile=json.loads(profile_path.read_text())
    audit=audit_profile(profile_path)
    saved=json.loads((root/spec['profile_audit']).read_text())
    if audit!=saved or not audit['qualified'] or audit['predictions_sha256']!=spec['profile_predictions_sha256']:
        raise ValueError('Independent qualified profile audit required')
    baseline=Path(profile['baseline_report'])
    old=json.loads(baseline.read_text())
    selected=old['selected']
    if len(selected)!=32 or len({r['id'] for r in selected})!=32:
        raise ValueError('Original unfiltered32family panel required')
    previous=json.loads((root/old['spec']['source_report']).read_text())
    training=json.loads(Path(previous['manifest_path']).read_text())
    items=load_conditions(training['config']['fragments'],[r['id'] for r in selected],'c20_center',cohort='train')
    return spec,profile,old,items


def summarize(records):
    summary=[]
    for pose in POSES:
        for arm in CONTEXTS:
            rows=[r for r in records if r['pose_arm']==pose and r['arm']==arm]
            if len(rows)!=128:
                raise ValueError('128 unfiltered cases per arm required')
            summary.append(dict(pose_arm=pose,arm=arm,samples=len(rows),
                physical=sum(r['refold_eligible_geometry'] for r in rows),
                steric_eligible=sum(r['steric_eligible'] for r in rows),
                eligible_families=len({r['family'] for r in rows if r['steric_eligible']}),
                overlap_cases=sum(r['nonbonded']['pairs_below_threshold']>0 for r in rows),
                median_motif_displacement_rmsd=float(np.median([r['solver']['motif_displacement_rmsd'] for r in rows])),
                median_torsion_rms_degrees=float(np.median([r['solver']['torsion_rms_degrees'] for r in rows]))))
    pairs=[]
    for arm in CONTEXTS:
        a={(r['target_id'],r['generation_slot']):r for r in records if r['pose_arm']=='fixed_pose' and r['arm']==arm}
        b={(r['target_id'],r['generation_slot']):r for r in records if r['pose_arm']=='free_pose' and r['arm']==arm}
        if len(a)!=128 or set(a)!=set(b):
            raise ValueError('Unmatched or duplicated paired cases')
        pairs.append(dict(arm=arm,
            gained=sum(not a[k]['steric_eligible'] and b[k]['steric_eligible'] for k in a),
            lost=sum(a[k]['steric_eligible'] and not b[k]['steric_eligible'] for k in a),
            retained=sum(a[k]['steric_eligible'] and b[k]['steric_eligible'] for k in a)))
    counts={(r['pose_arm'],r['arm']):r['steric_eligible'] for r in summary}
    qualified=(counts['free_pose','generated_cond']>=45
               and counts['free_pose','generated_cond']>counts['fixed_pose','generated_cond']
               and counts['free_pose','native_cond']>=124)
    return summary,pairs,qualified


def evaluate(root,protocol,output):
    tick=time.monotonic()
    spec,profile,old,items=inputs(root,protocol)
    deadline=tick+spec['cpu_seconds_cap']
    if spec['cpu_seconds_cap']!=7200:
        raise ValueError('Changed full CPU budget')
    output.mkdir(parents=True,exist_ok=False)
    snapshot=output/'source_snapshot'
    snapshot.mkdir()
    files=[Path(f) for f in profile['sources']]+[protocol,Path(__file__),root/'scripts/audit_movable_motif_closure.py']
    for file in files:
        (snapshot/file.name).write_bytes(file.read_bytes())
    source=Path(old['run'])/'predictions.h5'
    m=dict(status='running',profile_only=False,spec=spec,protocol=str(protocol.resolve()),
        protocol_sha256=sha(protocol),profile_report_sha256=sha(root/spec['profile_report']),
        profile_audit_sha256=sha(root/spec['profile_audit']),
        baseline_report=profile['baseline_report'],baseline_report_sha256=profile['baseline_report_sha256'],
        baseline_predictions_sha256=sha(source),sources={str(f.resolve()):sha(f) for f in files},
        selected=old['selected'],records=[],controls=profile['controls'],controls_reused_from=spec['profile_report'],
        matched_profile_outputs=0,run=str(output.resolve()))
    atomic_json(output/'manifest.json',m)
    profile_ids={r['id'] for r in profile['selected']}
    try:
        with h5py.File(source,'r',locking=False) as original, \
                h5py.File(Path(profile['run'])/'predictions.h5','r',locking=False) as small, \
                h5py.File(output/'predictions.h5','x',locking=False) as out:
            for row in old['selected']:
                ident,bucket=row['id'],row['bucket']
                item=items[ident]
                for arm in CONTEXTS:
                    for slot in range(4):
                        key=arm+'/'+ident+'/'+str(slot)
                        g=original[key]
                        parent,before=g['parent'][:],g['source'][:]
                        for pose in POSES:
                            result,stats=close_movable_motif(before,parent,item['start'],20,old['spec'],
                                free_pose=pose=='free_pose',deadline=deadline)
                            record=score(result,before,parent,dict(item,id=ident,arm=arm),slot,bucket,old['spec'],pose)
                            record['solver']=stats
                            m['records'].append(record)
                            group=out.require_group(pose+'/'+key)
                            for name,value in [('source',before),('parent',parent),('backbone',result)]:
                                group[name]=value
                            if ident in profile_ids:
                                if not np.array_equal(result,small[pose+'/'+key+'/backbone'][:]):
                                    raise ValueError('Full output differs from qualified profile')
                                m['matched_profile_outputs']+=1
                    out.flush()
                    atomic_json(output/'manifest.json',m)
                print(ident,'complete',len(m['records']),flush=True)
        if len(m['records'])!=512 or m['matched_profile_outputs']!=64:
            raise ValueError('Incomplete full or profile comparison')
        if sha(source)!=m['baseline_predictions_sha256'] or any(sha(Path(f))!=h for f,h in m['sources'].items()):
            raise ValueError('Changed inputs/scientific sources during assay')
        summary,pairs,qualified=summarize(m['records'])
        m.update(status='complete',summary=summary,paired=pairs,qualified=qualified,
            seconds=time.monotonic()-tick,solver_seconds=sum(r['solver']['seconds'] for r in m['records']),
            predictions_sha256=sha(output/'predictions.h5'))
    except Exception as exc:
        m.update(status='failed',error=repr(exc),seconds=time.monotonic()-tick)
        atomic_json(output/'manifest.json',m)
        raise
    atomic_json(output/'manifest.json',m)
    return dict(m,manifest_sha256=sha(output/'manifest.json'))


def audit_full(root,report):
    d=json.loads(report.read_text())
    run=Path(d['run'])
    if (d['status']!='complete' or d['profile_only'] or len(d['records'])!=512
            or sha(run/'manifest.json')!=d['manifest_sha256']
            or sha(run/'predictions.h5')!=d['predictions_sha256']
            or sha(Path(d['protocol']))!=d['protocol_sha256']):
        raise ValueError('Complete bound full report required')
    for file,digest in d['sources'].items():
        if sha(Path(file))!=digest or sha(run/'source_snapshot'/Path(file).name)!=digest:
            raise ValueError('Changed full scientific source/snapshot')
    spec,profile,old,items=inputs(root,Path(d['protocol']))
    if (d['spec']!=spec or d['selected']!=old['selected'] or d['controls']!=profile['controls']
            or len(d['controls'])!=16 or d['matched_profile_outputs']!=64):
        raise ValueError('Changed full panel, numerical controls or protocol')
    expected={(p,a,r['id'],s) for p in POSES for a in CONTEXTS for r in old['selected'] for s in range(4)}
    keys=[(r['pose_arm'],r['arm'],r['target_id'],r['generation_slot']) for r in d['records']]
    if len(set(keys))!=512 or set(keys)!=expected:
        raise ValueError('Missing, duplicated or substituted outputs')
    maximum,profile_matches=0.,0
    profile_ids={r['id'] for r in profile['selected']}
    with h5py.File(Path(old['run'])/'predictions.h5','r',locking=False) as original, \
            h5py.File(Path(profile['run'])/'predictions.h5','r',locking=False) as small, \
            h5py.File(run/'predictions.h5','r',locking=False) as f:
        for r in d['records']:
            key=r['arm']+'/'+r['target_id']+'/'+str(r['generation_slot'])
            fullkey=r['pose_arm']+'/'+key
            g=f[fullkey]
            parent,before,result=g['parent'][:],g['source'][:],g['backbone'][:]
            for name,value in [('parent',parent),('source',before)]:
                if not np.array_equal(value,original[key+'/'+name][:]):
                    raise ValueError('Changed original full input')
            item=dict(items[r['target_id']],id=r['target_id'],arm=r['arm'])
            s=r['solver']
            rebuilt=replay(before,parent,item['start'],20,old['spec'],s['torsion_offsets'],s['pose'],
                           free_pose=r['pose_arm']=='free_pose')
            error=float(np.max(np.abs(rebuilt-result)))
            maximum=max(maximum,error)
            if error!=0:
                raise ValueError('Saved parameters fail exact replay')
            scored=score(result,before,parent,item,r['generation_slot'],r['bucket'],old['spec'],r['pose_arm'])
            if scored!={k:v for k,v in r.items() if k!='solver'}:
                raise ValueError('NumPy geometry rescore differs')
            if r['target_id'] in profile_ids:
                if not np.array_equal(result,small[fullkey+'/backbone'][:]):
                    raise ValueError('Changed original profile output')
                profile_matches+=1
    summary,pairs,qualified=summarize(d['records'])
    if summary!=d['summary'] or pairs!=d['paired'] or qualified!=d['qualified'] or profile_matches!=64:
        raise ValueError('Changed qualification or summary')
    return dict(status='complete',records=512,controls=16,matched_profile_outputs=profile_matches,
        replay_max_abs=maximum,provenance_passed=True,rescore_passed=True,qualified=qualified,
        full_report_sha256=sha(report),manifest_sha256=d['manifest_sha256'],predictions_sha256=d['predictions_sha256'])


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--protocol',type=Path,default=Path('configs/movable_motif_full_protocol.json'))
    p.add_argument('--output',type=Path)
    p.add_argument('--audit',type=Path)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if bool(a.output)==bool(a.audit):
        p.error('Provide exactly one of --output or --audit')
    root=Path(__file__).resolve().parents[1]
    d=audit_full(root,a.audit) if a.audit else evaluate(root,a.protocol,a.output)
    atomic_json(a.report.with_suffix('.json'),d)
    if a.audit:
        lines=['# Full movable-motif audit','','```json',json.dumps(d,indent=2),'```','']
    else:
        lines=['# Full paired movable-motif CPU assay','',
            'Constructive feasibility; designability and learned capacity remain untested. All512outputs retained.','',
            '| Pose | Context | Physical /128 | Physical and overlap-free /128 | Families |',
            '|---|---|---:|---:|---:|']
        for r in d['summary']:
            lines.append(f"| {r['pose_arm']} | {r['arm']} | {r['physical']} | {r['steric_eligible']} | {r['eligible_families']} |")
        lines.extend(['',f"Qualified: {d['qualified']}; {d['seconds']:.2f} CPU seconds; no GPUs.",
            'All64profile outputs repeated exactly. Original isolated fragment remains the scoring reference.','',
            'Paired physical-and-overlap-free changes:','', '```json',json.dumps(d['paired'],indent=2),'```',''])
    a.report.with_suffix('.md').write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in d.items() if k in ('status','qualified','summary','paired','seconds','records') and k!='records'},indent=2))


if __name__=='__main__':main()
