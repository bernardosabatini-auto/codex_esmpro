"""Complete1024-output comparison; family-level paired contrasts within corpus size."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha


def clustered(values,seed=2026100351):
    x=np.asarray(values,float);rng=np.random.default_rng(seed)
    draws=x[rng.integers(len(x),size=(10000,len(x)))].mean(1)
    return dict(mean=float(x.mean()),ci95=np.quantile(draws,[.025,.975]).tolist(),families=len(x))


def summarize(screen,records,native):
    expected={(a,i,k) for a in ('control128','augmented128','control512','augmented512') for i in native for k in range(4)}
    keys=[(r['arm'],r['target_id'],r['generation_slot']) for r in screen]
    if len(native)!=64 or len(keys)!=1024 or set(keys)!=expected:raise ValueError('Changed complete denominator')
    outcomes={(r['arm'],r['target_id'],r['generation_slot']):r for r in records if r['arm']!='native'}
    selected={(r['arm'],r['target_id'],r['generation_slot']) for r in screen if r['raw_gate_passed']}
    if set(outcomes)!=selected or len(outcomes)!=sum(r['arm']!='native' for r in records):raise ValueError('Dropped or duplicate raw-match refold')
    enriched=[]
    for r in screen:
        q=outcomes.get((r['arm'],r['target_id'],r['generation_slot']),{})
        enriched.append(dict(r,strict_joint_success=q.get('strict_joint_success',False),scaffold_joint_success=q.get('scaffold_joint_success',False)))
    summaries=[];contrasts=[]
    for cohort in ('all','short','long'):
        rows=[r for r in enriched if cohort=='all' or (r['length']<=256 if cohort=='short' else r['length']>256)]
        for arm in ('control128','augmented128','control512','augmented512'):
            rr=[r for r in rows if r['arm']==arm];good=[r for r in rr if r['scaffold_joint_success']]
            if len(rr)!=(256 if cohort=='all' else 128):raise ValueError('Changed length stratum')
            summaries.append(dict(arm=arm,cohort=cohort,samples=len(rr),raw_matches=sum(r['raw_gate_passed'] for r in rr),primary_successes=sum(r['strict_joint_success'] for r in rr),scaffold_successes=len(good),successful_families=len({r['family'] for r in good}),successes_with_passing_native_control=sum(native[r['target_id']]['scaffold_joint_success'] for r in good)))
        for size in (128,512):
            families=sorted({r['family'] for r in rows});result=dict(training_proteins=size,cohort=cohort)
            for metric in ('raw_gate_passed','strict_joint_success','scaffold_joint_success'):
                delta=[np.mean([r[metric] for r in rows if r['family']==f and r['arm']==f'augmented{size}'])-np.mean([r[metric] for r in rows if r['family']==f and r['arm']==f'control{size}']) for f in families]
                result[metric]=clustered(delta)
            contrasts.append(result)
    return summaries,contrasts


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=4,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];ds=[];sources=[]
    for run in a.runs:
        path=root/'reports'/(run.name+'.json');d=json.loads(path.read_text())
        if d['status']!='complete' or d['manifest_sha256']!=sha(run/'manifest.json') or d['refolded_sha256']!=sha(run/'refolded.h5'):raise ValueError('Unaudited refold partition')
        ds.append(d);sources.append(dict(path=str(path),sha256=sha(path)))
    ids=[i for d in ds for i in d['target_ids']]
    if {d['partition'] for d in ds}!={0,1,2,3} or len(ids)!=64 or len(set(ids))!=64 or len({d['generation_inventory_sha256'] for d in ds})!=1:raise ValueError('Overlapping or mismatched partitions')
    native={i:r for d in ds for i,r in d['native_controls'].items()};records=[r for d in ds for r in d['records']];summaries,contrasts=summarize([r for d in ds for r in d['screen_rows']],records,native)
    if set(native)!=set(ids):raise ValueError('Missing native control')
    d=dict(status='complete',source_reports=sources,summaries=summaries,paired_family_contrasts=contrasts,native_controls=native,completed_refolds=sum(d['completed_refolds'] for d in ds),successful_scaffold_diversity=[r for d in ds for r in d['successful_scaffold_diversity']],scope='Additional development families; not a locked test. Same-refold scaffold success is the endpoint. All256outputs/model retained, with raw failures counted unsuccessful; their unconstrained designability is unmeasured. Bootstrap intervals describe family variation, not training-seed replication. Corpus-size comparisons have different parent histories and update counts. No evaluation labels enter training.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k not in ('native_controls','successful_scaffold_diversity')};a.output.with_suffix('.md').write_text('# Additional-family augmentation comparison\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
