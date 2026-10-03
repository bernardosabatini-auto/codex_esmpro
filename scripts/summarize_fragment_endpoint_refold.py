"""Same-valid-refold endpoint correction comparison, all16starts per arm."""
import argparse,json
from pathlib import Path
from prepare_fragment_endpoint_refold import audit_inputs
from fragment_refinement_core import score_assay
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    audit_inputs(m['config']);records=score_assay(run);summaries=[]
    for arm in ('native','initial','guided'):
        rr=[r for r in records if r['arm']==arm]
        if len(rr)!=(4 if arm=='native' else 16):raise ValueError('Changed denominator')
        summaries.append(dict(arm=arm,backbones=len(rr),raw_matches=sum(r['raw_gate_passed'] for r in rr),global_designable=sum(any(x['coarse_valid'] and x['sc_tm']>.5 for x in r['refolds']) for r in rr),strict_successes=sum(r['strict_joint_success'] for r in rr)))
    return dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),summaries=summaries,records=records,elapsed_seconds=m['elapsed_seconds'],scope='All16paired endpoints perarm and4fixed-motif native controls,8designs each,288refolds. No raw-pass filtering or pooled attempts. Same-refold scaffold supplement is required before improvement claims.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Validity-constrained endpoint refolding\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
