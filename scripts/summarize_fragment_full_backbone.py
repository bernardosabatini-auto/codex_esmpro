"""Same raw scaffolds, separate fixed sequence budgets, unchanged strict scoring."""
import argparse,json
from pathlib import Path
from fragment_refinement_core import score_assay
from prepare_fragment_full_backbone import audit_inputs
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json'
    if not path.exists():return dict(status='failed',error='Missing manifest')
    m=json.loads(path.read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];audit_inputs(c);rows=score_assay(run);old=c['baseline_records'];summary=[]
    for mode,records in [('ca_only',old),('full_backbone',rows)]:
        generated=[r for r in records if r['arm']!='native'];native=[r for r in records if r['arm']=='native']
        if len(generated)!=2 or len(native)!=2:raise ValueError('Incomplete comparison')
        summary.append(dict(mode=mode,backbones=2,sequences_per_backbone=8,strict_successes=sum(r['strict_joint_success'] for r in generated),valid_global=sum(r['valid_designable'] for r in generated),native_controls_passed=all(r['strict_joint_success'] for r in native)))
    return dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),new_refolds=32,reused_baseline_refolds=32,summaries=summary,records=rows,elapsed_seconds=m['elapsed_seconds'],interpretation=json.loads(Path(c['protocol']).read_text())['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Full-backbone sequence-design feasibility\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
