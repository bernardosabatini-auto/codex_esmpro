"""Join strict same-refold success to previously unfiltered diversity pairs."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from trajectory_guidance_refolding import add_summary


def main():
    p=argparse.ArgumentParser()
    for k in ('refold-report','diversity','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];run=root/'runs'/a.refold_report.stem;d=json.loads(a.refold_report.read_text());m=json.loads((run/'manifest.json').read_text());c=m['config'];v=json.loads(a.diversity.read_text());spec=json.loads(Path(c['protocol']).read_text())
    joint=bool(d.get('sequence_guidance_refold'))
    if d['status']!='complete' or d['manifest_sha256']!=sha(run/'manifest.json') or d['refolded_sha256']!=sha(run/'refolded.h5') or d['completed_refolds']!=(128 if joint else 288) or not (joint or d.get('trajectory_guidance_refold')):raise ValueError('Unaudited or changed full assay')
    if v['manifest_sha256']!=c['generation_manifest_sha256'] or v['predictions_sha256']!=c['generated_predictions_sha256'] or v['scorer_sha256']!=c['usalign_sha256']:raise ValueError('Diversity from different generation')
    records=d['records']+d.get('reused_baseline_records',[])
    check=dict(records=records);add_summary(check,spec)
    if check['summary']!=d['summary'] or check['qualified']!=d['qualified']:raise ValueError('Changed advancement decision')
    indexed={(r['arm'],r['target_id'],r['generation_slot']):r for r in records}
    rows=[]
    for r in v['records']:
        arm,ident=r['arm'],r['target_id'];i,j=r['slots'];rows.append(dict(r,both_strict=all(indexed[arm,ident,k]['scaffold_joint_success'] for k in (i,j))))
    if len(rows)!=48:raise ValueError('Missing raw diversity pairs')
    summaries=[]
    for arm in ('baseline','guided'):
        for subset in ('all','both_strict'):
            rr=[r for r in rows if r['arm']==arm and (subset=='all' or r['both_strict'])]
            summaries.append(dict(arm=arm,subset=subset,pairs=len(rr),families=len({r['target_id'] for r in rr}),mean_scaffold_tm=float(np.mean([r['scaffold_tm'] for r in rr])) if rr else None,mean_global_tm=float(np.mean([r['global_tm'] for r in rr])) if rr else None))
    paired=[]
    for (arm,ident,k),r in indexed.items():
        if arm=='guided':paired.append(dict(target_id=ident,slot=k,baseline_strict=indexed['baseline',ident,k]['scaffold_joint_success'],guided_strict=r['scaffold_joint_success'],baseline_designable=indexed['baseline',ident,k]['valid_designable'],guided_designable=r['valid_designable']))
    result=dict(status='complete',qualified=d['qualified'],summary=d['summary'],gates=d['advancement_gates'],diversity=summaries,paired=paired,refold_report_sha256=sha(a.refold_report),diversity_cache_sha256=sha(a.diversity),new_refolds=128 if joint else 288,reused_refolds=160 if joint else 0,scope='Four repeatedly used training families; fixed288refold budget. This is an inference-guidance pilot, not a newly trained model or independent benchmark. No historical sequence attempts pooled.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    visible={k:v for k,v in result.items() if k!='paired'};a.output.with_suffix('.md').write_text('# Mid-flow guidance: same-refold verdict\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))

if __name__=='__main__':main()
