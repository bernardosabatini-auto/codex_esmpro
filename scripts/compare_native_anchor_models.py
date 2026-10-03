"""All-output comparison of native-anchor pilots with the unchanged6000 parent."""
import argparse
import json
from pathlib import Path


def ready_command(root):
    path=root/'runs/native_anchor_model_comparison.json'
    output=root/'reports/native_anchor_model_comparison_20261003'
    if not path.exists() or output.with_suffix('.json').exists():return None
    plan=json.loads(path.read_text());jobs=plan['jobs']
    if set(jobs)!={'positive','contrastive'} or any(len(v)!=4 for v in jobs.values()):raise ValueError('Incomplete declared model comparison')
    ids=[i for v in jobs.values() for i in v]
    if len(set(ids))!=8:raise ValueError('Duplicate refold partitions')
    registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if any(i not in registry or registry[i]['completion_action']!='summarize_fragment_preference_refold' for i in ids):raise ValueError('Unregistered model refolds')
    paths=[root/f'reports/fragment_preference_refold_{i}.json' for i in ids]
    if not all(p.exists() and json.loads(p.read_text())['status']=='complete' for p in paths):return None
    return [str(root/'scripts/compare_native_anchor_models.py'),'--plan',str(path),'--output',str(output)]


def verify_outcome(r):
    from latentfold.fragment_designability import same_refold_success
    expected=same_refold_success(r['raw'],r['refolds'])
    for key,value in expected.items():
        if r[key]!=value:raise ValueError('Changed same-refold outcome: '+key)
    good=[k for k in expected['successful_refold_indices'] if r['refolds'][k]['scaffold_tm']>.5] if expected['raw_gate_passed'] else []
    if r['scaffold_successful_refold_indices']!=good or r['scaffold_joint_success']!=bool(good):
        raise ValueError('Scaffold and motif/global criteria do not share a refold')


def diversity(gc,records,usalign):
    import itertools
    import h5py
    import numpy as np
    from latentfold.metrics import usalign_coordinates
    successful={(r['target_id'],r['generation_slot']) for r in records if r['scaffold_joint_success']}
    path=Path(gc['generation_manifest']).parent/'predictions.h5';config=gc['config'];rows=[]
    with h5py.File(path) as f,h5py.File(config['fragments']) as fragments:
        for r in config['selected']:
            ident=r['id'];bb=f['new/'+ident+'/backbone'][:];q=fragments['train/'+ident+'/conditions/c20_center']
            mask=np.ones(r['length'],bool);start=int(q.attrs['start']);mask[start:start+20]=False
            for i,j in itertools.combinations(range(4),2):
                rows.append(dict(target_id=ident,bucket=r['bucket'],slots=[i,j],both_strong=(ident,i) in successful and (ident,j) in successful,
                                 global_tm=usalign_coordinates(usalign,bb[i,:,1],bb[j,:,1]),
                                 scaffold_tm=usalign_coordinates(usalign,bb[i,mask,1],bb[j,mask,1])))
    if len(rows)!=192:raise ValueError('Changed four-noise diversity inventory')
    summaries=[]
    for bucket in [None,128,256,384,512]:
        for subset in ('all','both_strong'):
            rr=[r for r in rows if (bucket is None or r['bucket']==bucket) and (subset=='all' or r['both_strong'])]
            summaries.append(dict(bucket=bucket,subset=subset,pairs=len(rr),proteins=len({r['target_id'] for r in rr}),
                                  mean_global_tm=float(np.mean([r['global_tm'] for r in rr])) if rr else None,
                                  mean_scaffold_tm=float(np.mean([r['scaffold_tm'] for r in rr])) if rr else None))
    return dict(summary=summaries,records=rows)


def compare(plan,root):
    import numpy as np
    from compare_extra_fragment_refolds import clustered
    from prepare_fragment_preference_refold import audit_inputs,TEACHER_KEYS
    from prepare_overfit import sha
    baseline=root/'reports/fragment_preference_comparison_20261003.json'
    if sha(baseline)!=plan['baseline_comparison_sha256']:raise ValueError('Changed original refold comparison')
    prior=json.loads(baseline.read_text())
    paths={'parent6000':[Path(r['report']) for r in prior['sources']]}
    paths.update({arm:[root/f'reports/fragment_preference_refold_{i}.json' for i in ids] for arm,ids in plan['jobs'].items()})
    arms={};sources=[];generations={};configs={}
    for arm,reports in paths.items():
        rows=[];parts=set();generation_hash=None
        for rp in reports:
            run=root/'runs'/rp.stem;mp=run/'manifest.json';m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];gc,spec=audit_inputs(c)
            if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp)
                    or d['refolded_sha256']!=sha(run/'refolded.h5') or d['completed_refolds']!=256
                    or len(d['records'])!=32 or c['partition'] in parts or d['partition']!=c['partition']
                    or d['generation_manifest_sha256']!=c['generation_manifest_sha256']
                    or not m['teacher_deterministic_algorithms'] or gc['arm']!=arm):raise ValueError('Incomplete or unmatched model partition')
            if generation_hash is not None and generation_hash!=c['generation_manifest_sha256']:raise ValueError('Mixed generations')
            generation_hash=c['generation_manifest_sha256'];parts.add(c['partition'])
            if [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]:raise ValueError('Changed record inventory')
            for r in d['records']:
                if r['arm']!=arm or len(r['refolds'])!=8:raise ValueError('Changed arm or refold budget')
                verify_outcome(r)
            rows.extend(d['records']);sources.append(dict(path=str(rp),sha256=sha(rp)))
            configs[arm,c['partition']]=c
            generations[arm]=dict(generation_manifest=c['generation_manifest'],config=gc)
        wanted={(r['id'],k) for r in gc['selected'] for k in range(4)}
        if parts!=set(range(4)) or len(rows)!=128 or {(r['target_id'],r['generation_slot']) for r in rows}!=wanted:raise ValueError('Changed full denominator')
        arms[arm]=rows
    base=generations['parent6000']['config']
    for arm in ('positive','contrastive'):
        gc=generations[arm]['config']
        if gc['selected']!=base['selected'] or gc['native_sources']!=base['native_sources']:raise ValueError('Changed targets or reused native budgets')
        if sha(generations[arm]['generation_manifest'])!=plan['generation_manifest_sha256'][arm]:raise ValueError('Changed declared generation')
        for part in range(4):
            a,b=configs[arm,part],configs['parent6000',part]
            if any(a[k]!=b[k] for k in TEACHER_KEYS):raise ValueError('Unmatched teacher/design recipe')
            fields=('target_id','family','length','generation_slot','fixed_start','fixed_sequence','repeatability_control')
            if any(x[k]!=y[k] for x,y in zip(a['entries'],b['entries']) for k in fields):raise ValueError('Unmatched refold inputs')
    summary=[];contrasts=[]
    for bucket in [None,128,256,384,512]:
        subsets={arm:[r for r in rows if bucket is None or r['bucket']==bucket] for arm,rows in arms.items()}
        for arm,rows in subsets.items():
            summary.append(dict(arm=arm,bucket=bucket,samples=len(rows),raw=sum(r['raw_gate_passed'] for r in rows),
                                strong=sum(r['scaffold_joint_success'] for r in rows),designable=sum(r['valid_designable'] for r in rows),
                                strong_families=len({r['family'] for r in rows if r['scaffold_joint_success']})))
        families=sorted({r['family'] for r in subsets['parent6000']})
        for candidate,reference in [('positive','parent6000'),('contrastive','parent6000'),('contrastive','positive')]:
            metrics={}
            for metric in ('raw_gate_passed','scaffold_joint_success','valid_designable'):
                delta=[np.mean([r[metric] for r in subsets[candidate] if r['family']==f])-np.mean([r[metric] for r in subsets[reference] if r['family']==f]) for f in families]
                metrics[metric]=clustered(delta)
            contrasts.append(dict(candidate=candidate,reference=reference,bucket=bucket,metrics=metrics))
    totals={r['arm']:r for r in summary if r['bucket'] is None};reference=totals['parent6000']
    qualified={arm:(totals[arm]['strong']>reference['strong'] and totals[arm]['designable']>=reference['designable'] and totals[arm]['strong_families']>=reference['strong_families']) for arm in ('positive','contrastive')}
    return dict(status='complete',training_only=True,source_reports=sources,summary=summary,contrasts=contrasts,
                development_screen_qualified=qualified,new_refolds=2048,reused_refolds=1024,native=prior['native'],
                diversity={arm:diversity(generations[arm],rows,configs[arm,0]['usalign']) for arm,rows in arms.items()},
                scope='Repeated32training-protein diagnostic; disjoint from16anchor-source proteins, not independent generalization. All128samples/arm and8designs/sample retained. Same valid refold must satisfy motif/global/scaffold gates. Native budgets reused unchanged; teacher RNG not claimed paired. Bootstrap describes family variation, not training-seed replication. Qualification permits a separate development assay only.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=compare(json.loads(a.plan.read_text()),Path(__file__).resolve().parents[1]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Native-anchor model diagnostic','',d['scope'],'','|Arm|Raw /128|Strong /128|Designable /128|Successful families|','|---|---:|---:|---:|---:|']
    for r in d['summary']:
        if r['bucket'] is None:lines.append(f"|{r['arm']}|{r['raw']}|{r['strong']}|{r['designable']}|{r['strong_families']}|")
    lines.extend(['','Development-screen qualification: '+json.dumps(d['development_screen_qualified'])])
    for r in d['contrasts']:
        if r['bucket'] is None:lines.extend(['',f"{r['candidate']} minus {r['reference']}, strict success: {r['metrics']['scaffold_joint_success']}"])
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(d['development_screen_qualified']))


if __name__=='__main__':main()
