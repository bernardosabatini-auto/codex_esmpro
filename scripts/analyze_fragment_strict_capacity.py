"""Apply the stricter proper-rotation motif criterion to all saved capacity samples."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sources=[];summaries=[];allrows=[]
    for run in a.runs:
        m=json.loads((run/'manifest.json').read_text());c=m['config']
        if m['status']!='complete' or m['updates']!=2000 or sha(c['fragments'])!=c['fragments_sha256']:raise ValueError('Completed unchanged source required')
        sources.append(dict(run=str(run),manifest_sha256=sha(run/'manifest.json'),predictions_sha256=sha(run/'evaluation_2000.h5')));rows=[]
        with h5py.File(c['fragments']) as fr,h5py.File(run/'evaluation_2000.h5') as f:
            for cohort in ('train','development'):
                for mode in ('conditioned','null'):
                    if set(f[cohort+'/'+mode])!=set(fr[cohort]):raise ValueError('Incomplete inventory')
                    for ident,g in f[cohort+'/'+mode].items():
                        q=fr[cohort+'/'+ident+'/conditions/f30_center'];bb=g['backbone'][:];valid=backbone_geometry(bb)['coarse_valid']
                        if len(bb)!=4:raise ValueError('Expected four fixed noises')
                        for k,x in enumerate(bb):
                            fit=motif_fit(x,q['fragment'][:],int(q.attrs['start']));rows.append(dict(run=run.name,cohort=cohort,mode=mode,target_id=ident,family=str(fr[cohort+'/'+ident].attrs['family']),slot=k,coarse_valid=bool(valid[k]),strict_raw=bool(valid[k] and fit['motif_drms']<=1 and fit['motif_ca_rmsd']<=1),**fit))
        if len(rows)!=384:raise ValueError('Incomplete evaluation')
        for cohort in ('train','development'):
            families=sorted({r['family'] for r in rows if r['cohort']==cohort});arms={}
            for mode in ('conditioned','null'):
                rr=[r for r in rows if (r['cohort'],r['mode'])==(cohort,mode)];arms[mode]=dict(samples=len(rr),valid=sum(r['coarse_valid'] for r in rr),strict_raw=sum(r['strict_raw'] for r in rr),families_with_strict_success=len({r['family'] for r in rr if r['strict_raw']}),mean_motif_ca_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])))
            delta=[np.mean([r['strict_raw'] for r in rows if (r['cohort'],r['mode'],r['family'])==(cohort,'conditioned',family)])-np.mean([r['strict_raw'] for r in rows if (r['cohort'],r['mode'],r['family'])==(cohort,'null',family)]) for family in families];summaries.append(dict(run=run.name,cohort=cohort,arms=arms,conditioned_minus_null=interval(delta)))
        allrows+=rows
    d=dict(status='complete',interpretation='Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.',sources=sources,summaries=summaries,records=allrows);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# Strict raw fragment capacity\n\n'+d['interpretation']+'\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
