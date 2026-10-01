"""Freeze nine-sample choices using predictions only, then score the fixed choices."""
import argparse, contextlib, json, time
from pathlib import Path
import h5py
import numpy as np
from analyze_consensus import digest
from latentfold.selection import ca_lddt_medoid
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores

ROOT=Path(__file__).resolve().parents[1]
SETTING='steps25_cfg2'


def select(protocol, output):
    if output.exists():raise FileExistsError(output)
    plan=json.loads(protocol.read_text());runs=[ROOT/path for path in plan['runs']]
    manifests=[json.loads((run/'manifest.json').read_text()) for run in runs]
    if len(runs)!=3 or [m['config']['seed'] for m in manifests]!=plan['seeds_in_order']:
        raise ValueError('incorrect three-run pool')
    reference=manifests[0];names=reference['config']['target_ids']
    if len(names)!=626 or len(set(names))!=626:raise ValueError('wrong target coverage')
    sources=[];priors=[]
    for run,m,path in zip(runs,manifests,plan['three_sample_choices']):
        if m['status']!='complete' or m['config']['samples']!=3:raise ValueError('incomplete prediction source')
        for key in ('checkpoint','decoder_checkpoint','dataset','precision'):
            if m[key]!=reference[key]:raise ValueError('pool changed '+key)
        for key in ('target_ids','samples','target_manifest_sha256','decoder_steps'):
            if m['config'][key]!=reference['config'][key]:raise ValueError('pool changed '+key)
        prior_path=ROOT/path;prior=json.loads(prior_path.read_text())
        source=dict(run=str(run),manifest_sha256=digest(run/'manifest.json'),predictions_sha256=digest(run/'predictions.h5'),prior_choices=str(prior_path),prior_choices_sha256=digest(prior_path))
        if prior['manifest_sha256']!=source['manifest_sha256'] or prior['predictions_sha256']!=source['predictions_sha256'] or prior['policy']!='ca_lddt_medoid_v1' or prior['setting']!=SETTING:
            raise ValueError('earlier three-sample choices do not match')
        priors.append(prior);sources.append(source)
    started=time.monotonic();rows={}
    with contextlib.ExitStack() as stack:
        handles=[stack.enter_context(h5py.File(run/'predictions.h5','r'))[SETTING] for run in runs]
        maps=[{g.attrs['target_id']:key for key,g in handle.items()} for handle in handles]
        if any(set(mapping)!=set(names) for mapping in maps):raise ValueError('prediction target coverage differs')
        for index,name in enumerate(names):
            groups=[handle[mapping[name]] for handle,mapping in zip(handles,maps)]
            if any(set(group)!={'0','1','2'} for group in groups):raise ValueError('wrong sample coverage')
            xyz=np.array([group[str(k)]['ca'][:] for group in groups for k in range(3)])
            trio=[ca_lddt_medoid(xyz[3*k:3*k+3])[0] for k in range(3)]
            if trio!=[prior['choices'][name]['sample'] for prior in priors]:raise ValueError('three-sample choice changed')
            sample,agreement,_=ca_lddt_medoid(xyz,expected_samples=9)
            rows[name]=dict(sample=sample,agreement=agreement,three_sample_choices=[3*k+v for k,v in enumerate(trio)])
            if (index+1)%100==0:print('frozen choices',index+1,flush=True)
    result=dict(status='complete',policy='ca_lddt_medoid_nine_v1',protocol=str(protocol.resolve()),protocol_sha256=digest(protocol),sources=sources,choices=rows,
        selection_seconds=time.monotonic()-started,note='Nine-sample choices written before opening native score files. Runtime includes HDF5 reads and three-sample parity checks; not optimized deployment latency.')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('choices','sources')}),flush=True)


def evaluate(choices_path,output):
    choices=json.loads(choices_path.read_text());protocol=Path(choices['protocol'])
    if digest(protocol)!=choices['protocol_sha256']:raise ValueError('selection protocol changed')
    plan=json.loads(protocol.read_text());cp=ROOT/plan['clusters']
    if digest(cp)!=plan['clusters_sha256']:raise ValueError('clusters changed')
    clusters=json.loads(cp.read_text())['clusters'];rows={name:[] for name in choices['choices']};scorer=None;generation_seconds=[]
    for source in choices['sources']:
        run=Path(source['run'])
        for filename,key in [('manifest.json','manifest_sha256'),('predictions.h5','predictions_sha256')]:
            if digest(run/filename)!=source[key]:raise ValueError('frozen input changed')
        if digest(Path(source['prior_choices']))!=source['prior_choices_sha256']:raise ValueError('three-sample choices changed')
        m=json.loads((run/'manifest.json').read_text());s=json.loads((run/'scores.json').read_text());validate_scores(m,s)
        if scorer is not None and scorer!=s['usalign']:raise ValueError('scoring protocol differs')
        scorer=s['usalign'];selected={(r['target_id'],r['sample']):r for r in s['records'] if r['setting']==SETTING}
        for name in rows:rows[name].extend(selected[name,k] for k in range(3))
        generation_seconds.append(sum(b['seconds_including_input_and_d2h'] for b in m['batches'] if b['setting']==SETTING))
    if set(rows)!=set(clusters):raise ValueError('cluster/target coverage mismatch')
    paired={};geometry={};fields=('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')
    for metric in ('tm_fixed_reference','ca_lddt',*fields):
        values=lambda row:row[metric]/max(1,row['reference_adjacent_short_count']) if metric in fields else row[metric]
        selected={name:values(samples[choices['choices'][name]['sample']]) for name,samples in rows.items()}
        baselines=dict(nine_sample_mean={name:float(np.mean([values(r) for r in samples])) for name,samples in rows.items()},
            three_sample_medoid_expectation={name:float(np.mean([values(samples[k]) for k in choices['choices'][name]['three_sample_choices']])) for name,samples in rows.items()})
        comparisons={label:paired_comparison(base,selected,clusters=clusters) for label,base in baselines.items()}
        (geometry if metric in fields else paired)[metric]=comparisons
    tm=paired['tm_fixed_reference']['three_sample_medoid_expectation'];lddt=paired['ca_lddt']['three_sample_medoid_expectation']
    eligible=(tm['theirs']>=.5782384930777423 and tm['theirs_minus_ours']>=.003 and tm['ci95'][0]>0 and lddt['ci95'][0]>=-.005 and all(v['three_sample_medoid_expectation']['ci95'][1]<=.001 for v in geometry.values()))
    result=dict(status='complete',choices_sha256=digest(choices_path),protocol_sha256=choices['protocol_sha256'],pairs=paired,geometry=geometry,
        eligible_for_new_noise_pool=eligible,accuracy_promotion=False,oracle_tm_only=float(np.mean([max(r['tm_fixed_reference'] for r in samples) for samples in rows.values()])),
        selection_seconds=choices['selection_seconds'],existing_generation_seconds_by_trio=generation_seconds,
        head_decoder_sample_budget_multiplier=3,additional_gpu_hours=0,final_test_scored=False)
    lines=['# Nine-sample consensus budget diagnostic','',choices['note'],'',
        'Exploratory reuse of three already examined noise groups and 626 development proteins. The three-sample reference is its expectation over the three groups; coordinates are never averaged. Nine-sample selection needs three times the head/decoder sample budget. ESMC can be reused.','',
        '| Metric | Reference | Reference mean | Selected nine | Change [95% cluster CI] |','|---|---|---:|---:|---|']
    for metric,comparisons in paired.items():
        for label,row in comparisons.items():lines.append(f"| {metric} | {label} | {row['ours']:.5f} | {row['theirs']:.5f} | {row['theirs_minus_ours']:+.5f} {row['ci95']} |")
    lines+=['',f'Eligible for a new nine-sample noise pool: {eligible}. Native-TM best-of-nine is an oracle upper bound only. No accuracy promotion or final-test scoring.','', '```json',json.dumps(result,indent=2),'```']
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(selected_tm=tm['theirs'],change_vs_three=tm['theirs_minus_ours'],eligible=eligible)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='phase',required=True)
    s=sub.add_parser('select');s.add_argument('--protocol',type=Path,required=True);s.add_argument('--output',type=Path,required=True)
    e=sub.add_parser('evaluate');e.add_argument('--choices',type=Path,required=True);e.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.phase=='select':select(a.protocol,a.output)
    else:evaluate(a.choices,a.output)
