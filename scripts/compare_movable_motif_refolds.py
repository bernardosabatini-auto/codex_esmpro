"""Matched same-refold outcome comparison, plus posthoc local-damage diagnostics."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.connected_refold import connected_outcome
from latentfold.local_closure import topology
from latentfold.backbone_sterics import steric_audit
from compare_native_anchor_models import verify_outcome
from compare_extra_fragment_refolds import clustered
from fragment_junction_core import flank_bonds
from prepare_fragment_preference_refold import TEACHER_KEYS
from prepare_overfit import sha


def local_diagnostics(bb,parent,start,width=8,length=20):
    residues=topology(len(bb),start,length,width)['residues'];atom_ids=np.array([4*r+a for r in residues for a in range(4)])
    all_ids=np.arange(len(bb)*4);moving=np.isin(all_ids,atom_ids)
    pair_mask=(abs(atom_ids[:,None]//4-all_ids[None,:]//4)>2)&((atom_ids[:,None]<all_ids[None,:])|~moving[None,:])
    def clashes(x):
        x=np.asarray(x,dtype=np.float64).reshape(-1,3)
        distances=np.linalg.norm(x[atom_ids,None]-x[None],axis=-1)[pair_mask]
        return dict(nonlocal_pairs_below_1p5A=int((distances<1.5).sum()),minimum_nonlocal_distance=float(distances.min()))
    def angles(x):
        quads=[quad for r in residues for quad in ((x[r-1,2],x[r,0],x[r,1],x[r,2]),(x[r,0],x[r,1],x[r,2],x[r+1,0]))]
        q=np.asarray(quads,dtype=np.float64);b0=q[:,1]-q[:,0];b1=q[:,2]-q[:,1];b2=q[:,3]-q[:,2]
        n0=np.cross(b0,b1);n1=np.cross(b1,b2)
        return np.arctan2((np.cross(n0,n1)*b1).sum(-1)/np.linalg.norm(b1,axis=-1),(n0*n1).sum(-1))
    delta=(angles(bb)-angles(parent)+np.pi)%(2*np.pi)-np.pi
    return dict(candidate=clashes(bb),parent=clashes(parent),phi_psi_rms_change_degrees=float(np.degrees(np.sqrt(np.mean(delta**2)))),
                phi_psi_max_change_degrees=float(np.degrees(np.abs(delta).max())))


def analyze(root,jobs):
    registry={j['id']:j for j in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if len(jobs)!=4 or len(set(jobs))!=4 or any(j not in registry or registry[j]['completion_action']!='summarize_fragment_preference_refold' for j in jobs):
        raise ValueError('Four distinct registered own refold jobs required')
    baseline_path=root/'reports/fragment_preference_comparison_20261003.json';baseline=json.loads(baseline_path.read_text())
    paths={'parent6000':[Path(s['report']) for s in baseline['sources']],
           'movable_motif':[root/f'reports/fragment_preference_refold_{j}.json' for j in jobs]}
    if baseline['status']!='complete' or any(sha(s['report'])!=s['report_sha256'] for s in baseline['sources']):raise ValueError('Changed baseline')
    arms={};configs={};sources=[];generation=None
    for arm,reports in paths.items():
        rows=[];parts=set()
        for path in reports:
            d=json.loads(path.read_text());run=root/'runs'/path.stem;m=json.loads((run/'manifest.json').read_text());c=m['config']
            if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(run/'manifest.json')
                    or d['refolded_sha256']!=sha(run/'refolded.h5') or sha(c['predictions'])!=c['predictions_sha256']
                    or d['completed_refolds']!=256 or len(d['records'])!=32 or d['partition']!=c['partition']
                    or c['partition'] in parts or not m['teacher_deterministic_algorithms']):raise ValueError('Changed or duplicate refold partition')
            if arm=='movable_motif':
                if not d.get('movable_motif_refold') or not m.get('cpu_preflight_file_identity_unchanged'):raise ValueError('Wrong assay')
                current=json.loads(Path(c['generation_report']).read_text())
                if sha(c['generation_report'])!=c['generation_report_sha256'] or sha(c['generated_predictions'])!=c['generated_predictions_sha256']:
                    raise ValueError('Changed constructive generation')
                if generation is not None and current!=generation:raise ValueError('Mixed constructed generations')
                generation=current
            parts.add(c['partition']);configs[arm,c['partition']]=c;sources.append(dict(path=str(path),sha256=sha(path)))
            with h5py.File(c['predictions'],'r',locking=False) as raw,h5py.File(run/'refolded.h5','r',locking=False) as folded:
                for r in d['records']:
                    if r['arm']!=arm:raise ValueError('Wrong output arm')
                    verify_outcome(r);bb=raw[r['dataset']][0]
                    edges=flank_bonds(bb,r['motif_start'],len(r['fixed_sequence']),8)
                    if arm=='parent6000':
                        movable=list(range(r['motif_start']-8,r['motif_start']+len(r['fixed_sequence'])+8))
                        atom=steric_audit(bb,movable)
                        r['raw_nonbonded']=atom
                        # Same atom exclusion/threshold as the candidate; parent-relative
                        # internal geometry is exactly unchanged for the original parent.
                        physical=bool(r['raw']['coarse_valid'] and edges['all_edges_valid'] and atom['pairs_below_threshold']==0)
                    else:physical=r['physical_raw']
                    for k,row in enumerate(r['refolds']):
                        row['flank_edges_valid']=flank_bonds(folded[r['name']+'/'+str(k)][:],r['motif_start'],len(r['fixed_sequence']),8)['all_edges_valid']
                    expected=connected_outcome(r['raw'],r['refolds'],physical_raw=physical)
                    if arm=='movable_motif' and any(r[k]!=v for k,v in expected.items()):raise ValueError('Changed same-refold outcome')
                    r.update(expected);rows.append(r)
        if parts!=set(range(4)) or len(rows)!=128 or len({(r['target_id'],r['generation_slot']) for r in rows})!=128:
            raise ValueError('Incomplete or duplicated full128-case denominator')
        arms[arm]=rows
    for p in range(4):
        a,b=configs['parent6000',p],configs['movable_motif',p]
        fields=('name','target_id','family','length','generation_slot','fixed_start','fixed_sequence','repeatability_control')
        if any(a[k]!=b[k] for k in TEACHER_KEYS) or any(x[k]!=y[k] for x,y in zip(a['entries'],b['entries']) for k in fields):
            raise ValueError('Unmatched teacher, sequences or candidates')
    by_arm={a:{(r['target_id'],r['generation_slot']):r for r in rows} for a,rows in arms.items()}
    if set(by_arm['parent6000'])!=set(by_arm['movable_motif']):raise ValueError('Different paired samples')
    summary=[];contrasts=[];metrics=('complete_strict','valid_designable','connected_designable','complete_connected_designable')
    for bucket in (None,128,256,384,512):
        subset={a:[r for r in rows if bucket is None or r['bucket']==bucket] for a,rows in arms.items()}
        for arm,rows in subset.items():summary.append(dict(arm=arm,bucket=bucket,samples=len(rows),
            **{k:sum(r[k] for r in rows) for k in metrics},strict_families=len({r['family'] for r in rows if r['complete_strict']})))
        families=sorted({r['family'] for r in subset['parent6000']})
        contrasts.append(dict(bucket=bucket,metrics={k:clustered([np.mean([r[k] for r in subset['movable_motif'] if r['family']==f])-
            np.mean([r[k] for r in subset['parent6000'] if r['family']==f]) for f in families]) for k in metrics}))
    candidate=next(r for r in summary if r['arm']=='movable_motif' and r['bucket'] is None)
    gate=dict(strict=candidate['complete_strict']>8,families=candidate['strict_families']>=7,
              designability=candidate['complete_connected_designable']>=45)
    damage=[]
    with h5py.File(Path(generation['run'])/'predictions.h5','r',locking=False) as f:
        for r in arms['movable_motif']:
            key=r['target_id'],r['generation_slot'];g=f['free_pose/generated_cond/'+key[0]+'/'+str(key[1])]
            damage.append(dict(target_id=key[0],slot=key[1],family=r['family'],physical=r['physical_raw'],
                designable=r['valid_designable'],strict=r['complete_strict'],parent_designable=by_arm['parent6000'][key]['valid_designable'],
                **local_diagnostics(g['backbone'][:],g['parent'][:],r['motif_start'])))
    diagnostic=[]
    for label,rr in [('all',damage),('physical',[r for r in damage if r['physical']]),
                     ('designable',[r for r in damage if r['designable']]),('not_designable',[r for r in damage if not r['designable']])]:
        diagnostic.append(dict(subset=label,samples=len(rr),candidate_atom_overlap_cases=sum(r['candidate']['nonlocal_pairs_below_1p5A']>0 for r in rr),
            parent_atom_overlap_cases=sum(r['parent']['nonlocal_pairs_below_1p5A']>0 for r in rr),
            median_phi_psi_change_degrees=float(np.median([r['phi_psi_rms_change_degrees'] for r in rr])) if rr else None))
    native=dict(budgets_reused=baseline['native_budgets_reused'],global_scaffold=baseline['native_global_scaffold'],controls=baseline['native'])
    return dict(status='complete',source_reports=sources,baseline_comparison_sha256=sha(baseline_path),summary=summary,contrasts=contrasts,
        gate=gate,qualified=all(gate.values()),completed_new_refolds=1024,reused_parent_refolds=1024,native=native,diagnostics=diagnostic,damage=damage,records=arms,
        scope='Movable-motif construction, with shared raw nonbonded exclusion/threshold for parent and candidate. Advancement still requires exceeding the original historical8strict and45designable counts. All128cases/arm; four distinct historical parent partitions, matched8attempt budgets. SAME-refold motif/global/scaffold/edge success, raw physical gate explicit. Posthoc atom-overlap/torsion diagnostics are descriptive, not new gates. Training-only; no learned-model or generalization claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--jobs',nargs=4,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(Path(__file__).resolve().parents[1],a.jobs);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    brief={k:v for k,v in d.items() if k not in ('records','damage','native')}
    a.output.with_suffix('.md').write_text('# Movable-motif designability comparison\n\n```json\n'+json.dumps(brief,indent=2)+'\n```\n')
    print(json.dumps(brief,indent=2))


if __name__=='__main__':main()
