"""Compare an EMA warm-started adaptation stage to its archived parent."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();new=json.loads((a.candidate/'manifest.json').read_text());c=new['config'];d=json.loads(a.report.read_text());base=json.loads(Path(c['warm_parent_manifest']).read_text())
    if new['status']!='complete' or new['updates']!=2000 or not c.get('warm_start') or c.get('expanded_fragment_data') or d['manifest_sha256']!=sha(a.candidate/'manifest.json') or d['status']!='complete':raise ValueError('Audited plain continuation required')
    if sha(c['warm_parent_manifest'])!=c['warm_parent_manifest_sha256'] or sha(c['warm_parent_report'])!=c['warm_parent_report_sha256'] or c['fragments_sha256']!=base['config']['fragments_sha256']:raise ValueError('Parent/data changed')
    if len(new['warm_controls'])!=384 or any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in new['warm_controls']):raise ValueError('Parent outputs not reproduced')
    previous=next(e['scores'] for e in base['evaluations'] if e['step']==2000);comparisons=[]
    for step in (500,2000):
        current=next(e['scores'] for e in new['evaluations'] if e['step']==step)
        for cohort in ('train','development'):
            families=sorted({r['family'] for r in previous if r['cohort']==cohort})
            for metric in ('joint','coarse_valid','motif_drms','ca_lddt'):
                def value(r):return float(r['coarse_valid'] and r['motif_drms']<=1) if metric=='joint' else r[metric]
                values=[[np.mean([value(r) for r in rows if (r['cohort'],r['mode'],r['family'])==(cohort,'conditioned',family)]) for family in families] for rows in (previous,current)]
                comparisons.append(dict(total_updates=2000+step,cohort=cohort,metric=metric,parent=float(np.mean(values[0])),candidate=float(np.mean(values[1])),candidate_minus_parent=interval(np.asarray(values[1])-values[0])))
    result=dict(status='complete',parent_updates=2000,candidate_total_updates=4000,initial_parent_samples_verified=384,manifest_sha256=sha(a.candidate/'manifest.json'),parent_manifest_sha256=c['warm_parent_manifest_sha256'],comparisons=comparisons);a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Additional isolated-fragment adaptation\n\nSame32training proteins and evaluation panel. Starts from parentEMA+adapter, with fresh optimizer and data/noise draws under a restarted schedule. This is additional adaptation, not an exact optimizer-state resume or a pure isolated step-count intervention. Parent failures remain reported. Strict proper-rotation and same-refold outcomes are audited separately.\n\n```json\n'+json.dumps(result,indent=2)+'\n```\n')

if __name__=='__main__':main()
