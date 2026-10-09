"""CPU-only fixed-panel profile of one atom-repulsion intervention."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np
from latentfold.steric_torsion_closure import close_steric_torsions,StericTorsionClosure
from latentfold.backbone_sterics import steric_audit
from latentfold.local_closure import topology
from evaluate_torsion_closure import score
from extra_fragment_validation_core import load_conditions
from profile_gpu import atomic_json
from prepare_overfit import sha


def evaluate(root,protocol,output):
    tick=time.monotonic();spec=json.loads(protocol.read_text());path=root/spec['baseline_report'];d=json.loads(path.read_text())
    old_spec=json.loads((root/spec['baseline_protocol']).read_text());source=Path(d['run'])/'predictions.h5'
    if (sha(path)!=spec['baseline_report_sha256'] or d['status']!='complete' or d['profile_only']
            or sha(source)!=d['predictions_sha256'] or d['spec']!=old_spec):raise ValueError('Bound full baseline required')
    ids=[next(r['id'] for r in d['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    selected=[r for r in d['selected'] if r['id'] in ids]
    previous=json.loads((root/old_spec['source_report']).read_text());training=json.loads(Path(previous['manifest_path']).read_text())
    items=load_conditions(training['config']['fragments'],ids,'c20_center',cohort='train')
    output.mkdir(parents=True,exist_ok=False);snapshot=output/'source_snapshot';snapshot.mkdir()
    files=[protocol,root/'src/latentfold/steric_torsion_closure.py',root/'src/latentfold/backbone_sterics.py',Path(__file__)]
    for file in files:(snapshot/file.name).write_bytes(file.read_bytes())
    m=dict(status='running',profile_only=True,protocol_sha256=sha(protocol),baseline_report_sha256=sha(path),
        baseline_predictions_sha256=sha(source),evidence_sha256={k:sha(root/spec[k]) for k in ('failure_evidence','steric_evidence')},
        sources={str(f):sha(f) for f in files},records=[],controls=[],selected=selected,spec=spec)
    atomic_json(output/'manifest.json',m);rng=np.random.default_rng(2026100801);deadline=tick+1200
    # No concurrent writers: source is immutable/checksummed and destination is exclusive.
    with h5py.File(source,'r',locking=False) as original,h5py.File(output/'predictions.h5','x',locking=False) as out:
        for row in selected:
            ident=row['id'];item=items[ident];start=item['start'];residues=topology(row['length'],start,20,8)['residues']
            for arm in ('generated_cond','native_cond'):
                for slot in range(4):
                    key=arm+'/'+ident+'/'+str(slot);g=original[key];parent=g['parent'][:];before=g['source'][:]
                    result,stats=close_steric_torsions(before,parent,start,20,old_spec,spec['nonbonded'],deadline=deadline)
                    r=score(result,before,parent,dict(item,id=ident,arm=arm),slot,row['bucket'],old_spec)
                    r['nonbonded']=steric_audit(result,residues);r['baseline_nonbonded']=steric_audit(g['backbone'][:],residues)
                    r['steric_eligible']=r['refold_eligible_geometry'] and r['nonbonded']['pairs_below_threshold']==0
                    r['solver']=stats;m['records'].append(r)
                    group=out.require_group(key)
                    for name,value in [('source',before),('parent',parent),('backbone',result)]:group[name]=value
                    if slot==0:
                        noop,ns=close_steric_torsions(parent,parent,start,20,old_spec,spec['nonbonded'],deadline=deadline)
                        repeat,_=close_steric_torsions(before,parent,start,20,old_spec,spec['nonbonded'],deadline=deadline)
                        q,_=np.linalg.qr(rng.normal(size=(3,3)));q[:,0]*=np.linalg.det(q);shift=rng.normal(size=3)*10
                        moved,_=close_steric_torsions(before@q+shift,parent@q+shift,start,20,old_spec,spec['nonbonded'],deadline=deadline)
                        control=dict(arm=arm,target_id=ident,noop_exact=bool(np.array_equal(noop,parent)),noop_calls=ns['closure_calls'],
                            repeat_exact=bool(np.array_equal(repeat,result)),pose_max_abs=float(np.max(np.abs(moved-result@q-shift))))
                        m['controls'].append(control)
                        if not control['noop_exact'] or control['noop_calls'] or not control['repeat_exact'] or control['pose_max_abs']>.005:
                            raise ValueError('No-op/repeat/pose control failed')
                    out.flush();atomic_json(output/'manifest.json',m)
                    print(arm,ident,slot,'steric_eligible',r['steric_eligible'],flush=True)
    if len(m['records'])!=32 or len(m['controls'])!=8:raise ValueError('Incomplete profile')
    summary=[]
    for arm in ('generated_cond','native_cond'):
        rr=[r for r in m['records'] if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rr),physical=sum(r['refold_eligible_geometry'] for r in rr),
            overlap_cases=sum(r['nonbonded']['pairs_below_threshold']>0 for r in rr),
            baseline_overlap_cases=sum(r['baseline_nonbonded']['pairs_below_threshold']>0 for r in rr),steric_eligible=sum(r['steric_eligible'] for r in rr)))
    m.update(status='complete',summary=summary,qualified=summary[0]['steric_eligible']>=12 and summary[1]['steric_eligible']==16,
        seconds=time.monotonic()-tick,predictions_sha256=sha(output/'predictions.h5'),run=str(output.resolve()))
    atomic_json(output/'manifest.json',m);return dict(m,manifest_sha256=sha(output/'manifest.json'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,default=Path('configs/steric_torsion_closure_protocol.json'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    d=evaluate(Path(__file__).resolve().parents[1],a.protocol,a.output)
    a.report.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');brief={k:v for k,v in d.items() if k not in ('records','spec','selected')}
    a.report.with_suffix('.md').write_text('# Atom-repulsion torsion-closure profile\n\n```json\n'+json.dumps(brief,indent=2)+'\n```\n')
    print(json.dumps(brief,indent=2))


if __name__=='__main__':main()
