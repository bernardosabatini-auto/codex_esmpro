"""Reload every saved closure, replay its torsions and independently rescore it."""
import argparse,json
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.torsion_closure import TorsionClosure
from evaluate_torsion_closure import score
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def audit(report):
    root=Path(__file__).resolve().parents[1];d=json.loads(report.read_text())
    run=Path(d['run']);manifest=run/'manifest.json';pred=run/'predictions.h5'
    if (d['status']!='complete' or sha(manifest)!=d['manifest_sha256'] or sha(pred)!=d['predictions_sha256']
            or sha(run/'source_snapshot/torsion_bridge_closure_protocol.json')!=d['protocol_sha256']
            or sha(run/'source_snapshot/torsion_closure.py')!=d['code_sha256']
            or sha(run/'source_snapshot/internal_bridge.py')!=d['kinematic_sha256']
            or sha(root/'src/latentfold/torsion_closure.py')!=d['code_sha256']
            or sha(root/'src/latentfold/internal_bridge.py')!=d['kinematic_sha256']
            or sha(root/'scripts/evaluate_torsion_closure.py')!=d['script_sha256']):
        raise ValueError('Changed complete closure data, protocol or source')
    spec=d['spec'];original=root/spec['source_report'];old=json.loads(original.read_text())
    if sha(original)!=d['source_report_sha256']:raise ValueError('Changed source run report')
    old_manifest=Path(old['manifest_path']);m=json.loads(old_manifest.read_text());op=old_manifest.parent/'predictions.h5'
    if sha(old_manifest)!=old['manifest_sha256'] or sha(op)!=d['source_predictions_sha256']:raise ValueError('Changed original data')
    ids=[r['id'] for r in d['selected']];buckets={r['id']:r['bucket'] for r in d['selected']}
    expected={(a,i,k) for a in spec['arms'] for i in ids for k in range(4)}
    actual={(r['arm'],r['target_id'],r['generation_slot']) for r in d['records']}
    if len(ids)!=(4 if d['profile_only'] else 32) or actual!=expected or len(d['records'])!=len(expected):
        raise ValueError('Filtered/incomplete closure panel')
    if len(d['controls'])!=8 or any(not c['noop_exact'] or not c['repeat_exact'] or c['noop_calls'] or c['pose_max_abs']>.005 for c in d['controls']):
        raise ValueError('Incomplete numerical controls')
    items=load_conditions(m['config']['fragments'],ids,'c20_center',cohort='train');max_replay=0.;max_endpoint=0.
    with h5py.File(pred) as f,h5py.File(op) as source:
        for r in d['records']:
            arm,ident,slot=r['arm'],r['target_id'],r['generation_slot'];g=f[arm+'/'+ident+'/'+str(slot)]
            parent=g['parent'][:];before=g['source'][:];output=g['backbone'][:];item=items[ident]
            old_parent=source[('parent' if arm=='generated_cond' else 'native_direct')+'/'+ident+'/backbone'][slot]
            expected_source=old_parent.astype(np.float64);expected_source-=expected_source.mean((0,1))
            known=source[arm+'/'+ident+'/coordinate_known'][slot];anchors=source[arm+'/'+ident+'/anchors'][slot]
            expected_source[known]=anchors[known]
            if not np.array_equal(parent,old_parent.astype(np.float64)) or not np.array_equal(before,expected_source):
                raise ValueError('Source is not original parent plus bound isolated anchors')
            # Reconstruct from recorded torsions without invoking the optimizer.
            start=item['start'];origin=parent[start,1]
            x=parent[start,2]-origin;x=x/np.linalg.norm(x)
            y=parent[start,0]-origin;y=y-np.dot(x,y)*x;y=y/np.linalg.norm(y)
            basis=np.stack((x,y,np.cross(x,y)),axis=1);grid=spec['solver']['input_grid_angstrom']
            problem=TorsionClosure(np.round(((before-origin)@basis)/grid)*grid,
                np.round(((parent-origin)@basis)/grid)*grid,start,spec['motif_length'],spec)
            delta=torch.tensor(r['solver']['torsion_offsets'],dtype=torch.float64)
            candidate,endpoint=problem.assemble(delta)
            replay=before.copy();editable=problem.graph['residues']
            if not r['solver']['exact_noop']:replay[editable]=candidate.detach().numpy()[editable]@basis.T+origin
            error=float(np.max(np.abs(replay-output)));max_replay=max(max_replay,error)
            e=float(np.max(np.abs(endpoint.square().sum(-1).mean(-1).sqrt().detach().numpy()-r['solver']['endpoint_rmsd_angstrom'])))
            max_endpoint=max(max_endpoint,e)
            if error>1e-10 or e>1e-10:raise ValueError('Stored torsions do not reproduce output or endpoint')
            measured=score(output,before,parent,dict(item,id=ident,arm=arm),slot,buckets[ident],spec)
            if measured!={k:v for k,v in r.items() if k!='solver'}:raise ValueError('Saved molecular geometry scores changed')
    summary=[]
    for arm in spec['arms']:
        rr=[r for r in d['records'] if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rr),coarse_valid=sum(r['coarse_valid'] for r in rr),
            local_geometry=sum(r['local_geometry']['valid'] for r in rr),
            all_flank_edges_valid=sum(r['hidden_flank_bonds']['all_edges_valid'] for r in rr),
            eligible=sum(r['refold_eligible_geometry'] for r in rr)))
    counts={r['arm']:r['eligible'] for r in summary}
    qualified=(counts['native_cond']>=12 and counts['generated_cond']>=1) if d['profile_only'] else counts['generated_cond']>=45
    if summary!=d['summary'] or qualified!=d['qualified']:raise ValueError('Qualification/counts changed')
    return dict(status='complete',qualified=qualified,profile_only=d['profile_only'],samples=len(d['records']),
        source_report_sha256=sha(report),predictions_sha256=sha(pred),max_replay_angstrom=max_replay,
        max_endpoint_replay_angstrom=max_endpoint,summary=summary,
        scope='Every unfiltered saved output replayed from its stored torsions and rescored for actual assembled geometry. Constructive feasibility only; no learned or refolded success claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=audit(a.report);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Independent torsion-closure audit\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')
    print(json.dumps(d,indent=2))


if __name__=='__main__':main()
