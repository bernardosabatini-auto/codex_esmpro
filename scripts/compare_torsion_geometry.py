"""Compare both constructions under the identical eight-flank physical gate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.local_closure import geometry_audit
from fragment_junction_core import flank_bonds
from compare_extra_fragment_refolds import clustered
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def analyze(report,audit_report):
    root=Path(__file__).resolve().parents[1];d=json.loads(report.read_text());audit=json.loads(audit_report.read_text())
    if (d['status']!='complete' or d['profile_only'] or audit['status']!='complete' or audit['profile_only']
            or audit['source_report_sha256']!=sha(report) or audit['samples']!=256):raise ValueError('Complete audited unfiltered panel required')
    old_report=root/'reports/local_closure_canonical_full_20261004.json';old=json.loads(old_report.read_text())
    old_manifest=Path(old['manifest_path']);om=json.loads(old_manifest.read_text())
    before=old_manifest.parent/'predictions.h5';after=Path(d['run'])/'predictions.h5'
    source=Path(om['config']['source_predictions']);sm=json.loads(Path(om['config']['source_manifest']).read_text())
    if (old['status']!='complete' or old['profile_only'] or old['manifest_sha256']!=sha(old_manifest)
            or old['predictions_sha256']!=sha(before) or d['predictions_sha256']!=sha(after)
            or sm['predictions_sha256']!=sha(source)):raise ValueError('Changed historical or current coordinates')
    selected=d['selected'];ids=[r['id'] for r in selected]
    items=load_conditions(sm['config']['fragments'],ids,'c20_center',cohort='train');rows=[]
    with h5py.File(before) as bf,h5py.File(after) as af,h5py.File(source) as original:
        for arm,parent in [('generated_cond','parent'),('native_cond','native_direct')]:
            old_rows=[r for r in old['records'] if r['arm']==arm];new_rows=[r for r in d['records'] if r['arm']==arm]
            wanted={(i,k) for i in ids for k in range(4)}
            if any(len(rr)!=128 or {(r['target_id'],r['generation_slot']) for r in rr}!=wanted for rr in (old_rows,new_rows)):
                raise ValueError('Changed paired denominator')
            for r in old_rows:
                ident,slot=r['target_id'],r['generation_slot'];item=items[ident]
                bb=bf[arm+'/'+ident+'/backbone'][slot];reference=original[parent+'/'+ident+'/backbone'][slot]
                candidate_parent=af[arm+'/'+ident+'/'+str(slot)+'/parent'][:]
                if not np.array_equal(candidate_parent,reference.astype(np.float64)):raise ValueError('Different original parent')
                local=geometry_audit(bb,reference,item['start'],20,8);edge=flank_bonds(bb,item['start'],20,8)
                eligible=bool(r['raw_gate_passed'] and r['junctions']['valid'] and local['valid'] and edge['all_edges_valid'])
                rows.append(dict(model='cartesian_then_four_residue_closure',arm=arm,target_id=ident,slot=slot,
                    eligible=eligible,original_four_residue_complete=r['qualified_raw']))
            for r in new_rows:
                rows.append(dict(model='torsion_closure',arm=arm,target_id=r['target_id'],slot=r['generation_slot'],eligible=r['refold_eligible_geometry']))
    summary=[];contrasts=[]
    lookup={(r['model'],r['arm'],r['target_id'],r['slot']):r['eligible'] for r in rows}
    for arm in ('generated_cond','native_cond'):
        for model in ('cartesian_then_four_residue_closure','torsion_closure'):
            rr=[r for r in rows if r['model']==model and r['arm']==arm]
            summary.append(dict(arm=arm,model=model,samples=len(rr),eligible=sum(r['eligible'] for r in rr)))
        differences=[np.mean([int(lookup['torsion_closure',arm,i,k])-int(lookup['cartesian_then_four_residue_closure',arm,i,k]) for k in range(4)]) for i in ids]
        contrasts.append(dict(arm=arm,eligible_difference=clustered(differences)))
    return dict(status='complete',source_report_sha256=sha(report),audit_report_sha256=sha(audit_report),
        baseline_report_sha256=sha(old_report),summary=summary,contrasts=contrasts,rows=rows,
        scope='All128cases per arm, same originals/fragments/noises. BOTH methods rescored for complete geometry across eight flanks. The old four-residue recipe/results remain unchanged. Multiple aspects of these constructions differ; this is not a learned-model ablation or designability/generalization evidence.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.report,a.audit)
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Matched physical-feasibility comparison\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='rows'},indent=2)+'\n```\n')
    print(json.dumps({k:v for k,v in d.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
