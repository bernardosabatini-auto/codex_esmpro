"""Bound CPU-only bridge feasibility; retain every failure and every output."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.torsion_closure import close_torsions
from latentfold.local_closure import geometry_audit,topology
from latentfold.fragment_inpainting import place_fragment
from latentfold.scaffold_bridge import scaffold_anchors
from fragment_junction_core import flank_bonds
from fragment_validation_core import raw_rows
from audit_inpainting_junctions import junctions
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha
from native_anchor_training_core import atomic_json


def score(output,source,parent,item,slot,bucket,spec):
    start=item['start'];length=spec['motif_length'];width=spec['flank_width']
    raw=raw_rows(output[None],item['fragment'],start,item['arm'],item['id'],item['family'])[0]
    local=geometry_audit(output,parent,start,length,width)
    edges=flank_bonds(output,start,length,width);junction=junctions(output,start,length)
    fixed=np.ones(len(source),dtype=bool);fixed[topology(len(source),start,length,width)['residues']]=False
    if not np.array_equal(output[fixed],source[fixed]):raise ValueError('Fixed requested motif/far scaffold moved')
    return dict(raw,generation_slot=slot,bucket=bucket,local_geometry=local,hidden_flank_bonds=edges,
        junctions=junction,fixed_exact=True,refold_eligible_geometry=bool(raw['raw_gate_passed'] and local['valid']
            and edges['all_edges_valid'] and junction['valid']))


def evaluate(root,protocol,output,profile_only,profile_report):
    tick=time.monotonic();spec=json.loads(protocol.read_text());report=root/spec['source_report']
    d=json.loads(report.read_text());mp=Path(d['manifest_path']);m=json.loads(mp.read_text());c=m['config']
    preflight=root/spec['representation_report'];pr=json.loads(preflight.read_text())
    pred=mp.parent/'predictions.h5';code=root/'src/latentfold/torsion_closure.py';kinematic=root/'src/latentfold/internal_bridge.py'
    if (sha(report)!=spec['source_report_sha256'] or d['status']!='complete' or d['qualified']
            or not d['scaffold_bridge'] or not d['numerically_qualified'] or sha(mp)!=d['manifest_sha256']
            or sha(pred)!=d['predictions_sha256'] or pr['status']!='complete' or not pr['qualified']
            or pr['code_sha256']!=sha(kinematic) or pr['protocol_sha256']!=sha(root/spec['representation_protocol'])
            or any(s['bridges']!=512 or s['passed']!=512 for s in pr['summary'])):
        raise ValueError('Bound failed candidate and complete numerical preflight required')
    selected=c['selected'];profile_ids=[next(r['id'] for r in selected if r['bucket']==b) for b in (128,256,384,512)]
    if len(selected)!=32 or len(set(profile_ids))!=4:raise ValueError('Wrong full or profile panel')
    if profile_only:selected=[r for r in selected if r['id'] in profile_ids]
    else:
        if profile_report is None:raise ValueError('Full CPU assay requires profile report')
        prof=json.loads(profile_report.read_text())
        if (prof['status']!='complete' or not prof['profile_only'] or not prof['qualified']
                or prof['protocol_sha256']!=sha(protocol) or prof['code_sha256']!=sha(code)
                or prof['kinematic_sha256']!=sha(kinematic) or prof['script_sha256']!=sha(Path(__file__))):
            raise ValueError('Matching qualified profile required')
    output.mkdir(parents=True,exist_ok=False)
    snapshot=output/'source_snapshot';snapshot.mkdir()
    for file in (protocol,code,kinematic,Path(__file__)):(snapshot/file.name).write_bytes(file.read_bytes())
    manifest=dict(status='running',profile_only=profile_only,protocol_sha256=sha(protocol),spec=spec,
        source_report_sha256=sha(report),source_predictions_sha256=sha(pred),representation_report_sha256=sha(preflight),
        code_sha256=sha(code),kinematic_sha256=sha(kinematic),script_sha256=sha(Path(__file__)),selected=selected,
        records=[],controls=[],profile_report=str(profile_report) if profile_report else None)
    atomic_json(output/'manifest.json',manifest)
    items=load_conditions(c['fragments'],[r['id'] for r in selected],'c20_center',cohort='train')
    deadline=tick+spec['cpu_profile_seconds_cap' if profile_only else 'cpu_full_seconds_cap']
    rng=np.random.default_rng(2026100492)
    with h5py.File(pred) as f,h5py.File(output/'predictions.h5','w') as out:
        for selected_row in selected:
            ident=selected_row['id'];item=items[ident];start=item['start'];length=spec['motif_length']
            for arm in spec['arms']:
                parent_arm='parent' if arm=='generated_cond' else 'native_direct'
                originals=f[parent_arm+'/'+ident+'/backbone'][:]
                expected=scaffold_anchors(torch.from_numpy(originals),
                    place_fragment(torch.from_numpy(item['fragment']),torch.from_numpy(originals),start),
                    item['keep'][None].expand(4,-1)).numpy()
                anchors=f[arm+'/'+ident+'/anchors'][:]
                known=f[arm+'/'+ident+'/coordinate_known'][:]
                if np.max(np.abs(anchors-expected))>1e-5:raise ValueError('Changed requested fragment/far anchors')
                for slot in range(4):
                    parent=originals[slot].astype(np.float64)
                    source=parent-parent.mean((0,1));source[known[slot]]=anchors[slot][known[slot]]
                    result,stats=close_torsions(source,parent,start,length,spec,deadline=deadline)
                    row=score(result,source,parent,dict(item,id=ident,arm=arm),slot,selected_row['bucket'],spec)
                    row['solver']=stats;manifest['records'].append(row)
                    group=out.require_group(arm+'/'+ident+'/'+str(slot))
                    for name,value in [('source',source),('parent',parent),('backbone',result)]:group[name]=value
                    if slot==0 and ident in profile_ids:
                        noop,noop_stats=close_torsions(parent,parent,start,length,spec,deadline=deadline)
                        again,_=close_torsions(source,parent,start,length,spec,deadline=deadline)
                        q,_=np.linalg.qr(rng.normal(size=(3,3)));q[:,0]*=np.linalg.det(q);shift=rng.normal(size=3)*10
                        transformed,_=close_torsions(source@q+shift,parent@q+shift,start,length,spec,deadline=deadline)
                        pose=float(np.max(np.abs(transformed-result@q-shift)))
                        control=dict(arm=arm,target_id=ident,noop_exact=bool(np.array_equal(noop,parent)),
                            noop_calls=noop_stats['closure_calls'],repeat_exact=bool(np.array_equal(again,result)),pose_max_abs=pose)
                        manifest['controls'].append(control)
                        if not control['noop_exact'] or control['noop_calls']!=0 or not control['repeat_exact'] or pose>.005:
                            raise ValueError('No-op, repetition or proper-pose control failed')
                    out.flush();atomic_json(output/'manifest.json',manifest)
                    print(arm,ident,slot,'eligible',row['refold_eligible_geometry'],flush=True)
    if len(manifest['records'])!=len(selected)*8 or len(manifest['controls'])!=8:raise ValueError('Incomplete unfiltered assay')
    if not profile_only:
        with h5py.File(output/'predictions.h5') as f,h5py.File(Path(prof['run'])/'predictions.h5') as old:
            for row in prof['records']:
                key=row['arm']+'/'+row['target_id']+'/'+str(row['generation_slot'])+'/backbone'
                if not np.array_equal(f[key][:],old[key][:]):raise ValueError('Profile/full output changed')
    summaries=[]
    for arm in spec['arms']:
        rr=[r for r in manifest['records'] if r['arm']==arm]
        summaries.append(dict(arm=arm,samples=len(rr),coarse_valid=sum(r['coarse_valid'] for r in rr),
            local_geometry=sum(r['local_geometry']['valid'] for r in rr),
            all_flank_edges_valid=sum(r['hidden_flank_bonds']['all_edges_valid'] for r in rr),
            eligible=sum(r['refold_eligible_geometry'] for r in rr)))
    counts={r['arm']:r['eligible'] for r in summaries}
    qualified=(counts['native_cond']>=12 and counts['generated_cond']>=1) if profile_only else counts['generated_cond']>=45
    manifest.update(status='complete',qualified=qualified,summary=summaries,seconds=time.monotonic()-tick,
        solver_seconds=sum(r['solver']['seconds'] for r in manifest['records']),predictions_sha256=sha(output/'predictions.h5'),run=str(output.resolve()))
    atomic_json(output/'manifest.json',manifest)
    return dict(manifest,manifest_path=str((output/'manifest.json').resolve()),manifest_sha256=sha(output/'manifest.json'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,default=Path('configs/torsion_bridge_closure_protocol.json'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--profile-only',action='store_true');p.add_argument('--profile-report',type=Path);a=p.parse_args()
    result=evaluate(Path(__file__).resolve().parents[1],a.protocol,a.output,a.profile_only,a.profile_report)
    a.report.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    brief={k:v for k,v in result.items() if k not in ('records','selected','spec')}
    a.report.with_suffix('.md').write_text('# Torsion bridge closure\n\nConstructive CPU feasibility; not learned capacity or designability.\n\n```json\n'+json.dumps(brief,indent=2)+'\n```\n')
    print(json.dumps(brief,indent=2))


if __name__=='__main__':main()
