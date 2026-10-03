"""Preserve overlapping cohort denominators for same-refold scaffold success."""
import argparse,json
from pathlib import Path
from fragment_validation_core import view_rows
from prepare_overfit import sha
from score_fragment_scaffold_supplement import analyze as score_scaffolds


def summarize_views(primary,scaffold,spec):
    rows=scaffold['rows'];keys=set();success=set()
    for r in primary['records']:
        key=(r['arm'],r['target_id'],r['generation_slot'])
        if key in keys:raise ValueError('Duplicate primary backbone')
        keys.add(key)
        rr=[x for x in rows if (x['arm'],x['target_id'],x['generation_slot'])==key]
        if len(rr)!=8 or {x['sequence_index'] for x in rr}!=set(range(8)):raise ValueError('Changed eight-design inventory')
        for x in rr:
            expected=r['raw_gate_passed'] and x['sequence_index'] in r['successful_refold_indices']
            if x['primary_joint_success']!=expected or x['scaffold_joint_success']!=(expected and x['scaffold_only_tm']>.5):raise ValueError('Combined different refolds or changed endpoint')
        if any(x['scaffold_joint_success'] for x in rr):success.add(key)
    if {(x['arm'],x['target_id'],x['generation_slot']) for x in rows}!=keys:raise ValueError('Added supplemental backbone')
    native={ident:('native',ident,slot) in success for arm,ident,slot in keys if arm=='native'}
    summaries=[]
    for p in primary['summaries']:
        rr=view_rows(primary['records'],p['arm'],p['view'],spec['focus_id'])
        good=[r for r in rr if (r['arm'],r['target_id'],r['generation_slot']) in success]
        expected=64 if p['view']=='whole_panel' else 16
        if p['screened']!=expected:raise ValueError('Changed screening denominator')
        summaries.append(dict(arm=p['arm'],view=p['view'],screened=expected,raw_matches=p['raw_matches'],primary_successes=p['strict_successes'],scaffold_successes=len(good),scaffold_fraction=len(good)/expected,successful_families=len({r['family'] for r in good}),successes_with_passing_native_control=sum(native[r['target_id']] for r in good)))
    return dict(summaries=summaries,native_scaffold_controls=native,successful_scaffold_diversity=scaffold['successful_scaffold_diversity'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    primary=json.loads(a.report.read_text());m=json.loads((a.run/'manifest.json').read_text());spec=json.loads(Path(m['config']['protocol']).read_text());scaffold=score_scaffolds(a.run,a.report)
    result=dict(status='complete',source_report_sha256=sha(a.report),manifest_sha256=sha(a.run/'manifest.json'),refolded_sha256=sha(a.run/'refolded.h5'),**summarize_views(primary,scaffold,spec),scaffold_evidence=scaffold,scope='Same valid refold must satisfy motif, global and scaffold agreement. Whole64and focus16overlap by4and must not be pooled. Diversity uses the first qualifying refold per distinct backbone; fewer than two backbones means undefined. Development feasibility only.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Fresh-noise same-refold scaffold agreement\n\n'+result['scope']+'\n\n```json\n'+json.dumps({k:result[k] for k in ('summaries','native_scaffold_controls','successful_scaffold_diversity')},indent=2)+'\n```\n')
    print(json.dumps(result['summaries']))

if __name__=='__main__':main()
