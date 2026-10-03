"""Retrospective native-anchor feasibility; never qualifies training labels."""
import argparse
import json
from pathlib import Path

from latentfold.fragment_preferences import motif_quality, split_preference
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=json.loads(a.comparison.read_text())
    if d['status']!='complete' or d['generated']!=128 or d['refolds']!=1024:raise ValueError('Incomplete collection')
    records=[];gc=None
    for source in d['sources']:
        if sha(source['manifest'])!=source['manifest_sha256'] or sha(source['report'])!=source['report_sha256']:raise ValueError('Changed comparison evidence')
        report=json.loads(Path(source['report']).read_text());records.extend(report['records'])
        m=json.loads(Path(source['manifest']).read_text())
        gc=json.loads(Path(m['config']['generation_manifest']).read_text())['config']
    params={k:gc['spec']['preference'][k] for k in ('minimum_quality','discovery_margin','confirmation_margin')}
    rows=[]
    for selected in gc['selected']:
        report=json.loads(Path(selected['native_report']).read_text())
        source=next(s for s in gc['native_sources'] if s['report']==selected['native_report'])
        bound=next(s for s in gc['sources'] if s['path']==selected['native_report'])
        if sha(selected['native_report'])!=bound['sha256'] or report['manifest_sha256']!=sha(source['manifest']):raise ValueError('Changed native reference')
        native=next(r for r in report['records'] if r['name']==selected['native_name'])
        native=dict(native,slot=-1,refolds=[dict(r,scaffold_tm=native['scaffold_scores'][k]) for k,r in enumerate(native['refolds'])])
        candidates=[dict(r,slot=r['generation_slot']) for r in records if r['target_id']==selected['id']]
        if len(candidates)!=4:raise ValueError('Changed candidate budget')
        # Force a native versus generated contrast; choose the negative with discovery designs only.
        loser=min(candidates,key=lambda r:(motif_quality(r,range(4)),r['slot']))
        preference=split_preference([native,loser],**params)
        rows.append(dict(target_id=selected['id'],bucket=selected['bucket'],
                         native_preferred=preference['winner']==-1,**{k:v for k,v in preference.items() if k!='target_id'}))
    result=dict(status='complete',comparison_sha256=sha(a.comparison),original_generated_preference_gate=d['gate'],
                proteins=32,native_preferred_discovery=sum(r['eligible'] and r['native_preferred'] for r in rows),
                native_preferred_confirmed=sum(r['confirmed'] and r['native_preferred'] for r in rows),records=rows,
                scope='Posthoc hypothesis audit only. Original generated-candidate gate is unchanged. Native coordinates have measured refolds, but their encoded latent plus stochastic decoder must be qualified before transferring positive labels. These pairs are not authorized training labels.',
                next='If native anchors supply stable contrasts, prospectively test decoded-native positive anchors on a separate training cohort. Compare positive-only replay with reference-anchored contrastive learning only after that independent label qualification.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    view={k:v for k,v in result.items() if k!='records'}
    a.output.with_suffix('.md').write_text('# Retrospective native-anchor feasibility\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')
    print(json.dumps(view))


if __name__=='__main__':main()
