"""Recompute all three-round outcomes without mixing refolds or budgets."""
import argparse,json
from pathlib import Path
from fragment_refinement_core import audit_config,score_assay,choose_refold
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json'
    if not path.exists():return dict(status='failed',error='Missing manifest')
    m=json.loads(path.read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),completed_rounds=len(m['rounds']))
    c=m['config'];audit_config(c)
    if [r['round'] for r in m['rounds']]!=c['spec']['rounds'] or m['training_updates_executed']:raise ValueError('Changed round inventory')
    initial={r['target_id']:r['initial'] for r in c['cases']};rows=[];controls=[]
    for r in m['rounds']:
        k=r['round'];assay=run/f'assay_{k}';gen=run/f'generation_{k}'
        if sha(assay/'manifest.json')!=r['assay_manifest_sha256'] or sha(assay/'refolded.h5')!=r['refolded_sha256'] or sha(gen/'manifest.json')!=r['generation_manifest_sha256']:raise ValueError('Changed round output')
        actual=score_assay(assay)
        if actual!=r['records']:raise ValueError('Changed audited metrics')
        gm=json.loads((gen/'manifest.json').read_text());fb=json.loads((run/f'feedback_{k}.json').read_text())
        if sha(run/f'feedback_{k}.json')!=gm['feedback_sha256']:raise ValueError('Changed feedback')
        for entry in actual:
            if entry['arm']=='feedback':
                previous=initial[entry['target_id']] if k==2 else next(x for x in rows if x['round']==2 and x['target_id']==entry['target_id'] and x['arm']=='feedback')
                # Previous records gain only a display round field in this report.
                expected={key:value for key,value in previous.items() if key!='round'}
                if fb[entry['target_id']]['record']!=expected:raise ValueError('Feedback lineage mismatch')
                choice=next(x for x in gm['records'] if x['name']==entry['name'])['selected_refold']
                if choice!=choose_refold(previous['refolds']):raise ValueError('Reference-dependent selection')
            rows.append(dict(round=k,**entry))
        controls.extend(dict(round=k,**x) for x in actual if x['arm']=='native')
    summary=[]
    for arm in ('feedback','random'):
        rr=[x for x in rows if x['arm']==arm]
        summary.append(dict(arm=arm,paths=2,designs_per_path_including_initial=24,
            round2_strict=sum(x['strict_joint_success'] for x in rr if x['round']==2),
            round3_strict=sum(x['strict_joint_success'] for x in rr if x['round']==3),
            cumulative_strict=sum(any(x['strict_joint_success'] for x in rr if x['target_id']==ident) or initial[ident]['strict_joint_success'] for ident in initial),
            valid_global_backbones=sum(x['valid_designable'] for x in rr)))
    return dict(status='complete',manifest_sha256=sha(path),summaries=summary,native_controls_passed=all(x['strict_joint_success'] for x in controls),new_refolds=96,reused_initial_generated_refolds=16,records=rows,elapsed_seconds=m['elapsed_seconds'],interpretation=c['spec']['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# Refold and recondition feasibility\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
