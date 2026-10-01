"""Compare explicit single-factor recovery runs with saved matched controls."""
import argparse
import hashlib
import json
from pathlib import Path
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores,means_by_target,hardware
from summarize_pilot import validate_training_evaluation,geometry_by_target,METRICS


def validate_pair(training,control):
    config=training['config'];task=training['task'];name=task['name']
    allowed={'optimizer_beta':{'optimizer_betas'},'residue_reduction':{'flow_config'},
        'broader_training_pool':{'training_manifest','training_manifest_sha256'}}
    overrides=task.get('overrides',{})
    if name not in allowed or set(overrides)!=allowed[name]:raise ValueError('undeclared recovery change')
    ignored={'tasks','matched_control_runs','gradient_controls','training_minutes','recovery_protocol',
             'holdout_manifest','holdout_manifest_sha256','test_note'}
    expected={**control['config'],**overrides}
    if {k:v for k,v in config.items() if k not in ignored}!={k:v for k,v in expected.items() if k not in ignored}:
        raise ValueError('training differs beyond the declared single factor')
    if training['status']!='complete' or training['steps']!=500 or control['status']!='complete' or control['steps']!=500:
        raise ValueError('incomplete training')
    if control['task']!={'seed':task['seed'],'arm':'flow'} or task['arm']!='flow':raise ValueError('wrong paired control')
    if len(training.get('gradient_controls',[]))!=4 or not all(c['passed'] for c in training['gradient_controls']):
        raise ValueError('missing or failed training gradient controls')
    keys=['step','bucket','batch','flow_rng_sha256']
    if name!='broader_training_pool':keys.append('input_ids_sha256')
    signature=lambda t:[tuple(r[k] for k in keys) for r in t['rows']]
    if signature(training)!=signature(control):raise ValueError('paired draws, batches or inputs changed')


def evaluate(run,training=None):
    m=json.loads((run/'manifest.json').read_text());s=json.loads((run/'scores.json').read_text())
    if training is None:validate_scores(m,s)
    else:validate_training_evaluation(training,m,s)
    return m,s


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=dict(status='complete',runs={},failures=[],accuracy_promotion=False)
    lines=['# Continued-training recovery screen','',
        'Exploratory single-factor tests; 500 updates. Reuse the original paired control. All 626 development proteins, three samples each, strict FP32 evaluation. The final test remains unscored.','',
        '| Arm | Seed | Mean TM | Change vs trained control [95% cluster CI] | Change vs untouched | Recovery screen |',
        '|---|---:|---:|---|---:|---|']
    for run in a.runs:
        try:
            t=json.loads((run/'training.json').read_text());cfg=t['config'];task=t['task']
            path=Path(cfg['matched_control_runs'][str(task['seed'])]);ct=json.loads((path/'training.json').read_text());validate_pair(t,ct)
            cp=Path(cfg['development_clusters'])
            if hashlib.sha256(cp.read_bytes()).hexdigest()!=cfg['development_clusters_sha256']:raise ValueError('development clusters changed')
            clusters=json.loads(cp.read_text())['clusters']
            m,s=evaluate(run/'evaluation',t);cm,cs=evaluate(path/'evaluation',ct);bm,bs=evaluate(Path(cfg['reference_run']))
            signature=lambda m,s:(m['dataset'],m['decoder_checkpoint'],m['precision'],s['usalign'])
            if signature(m,s)!=signature(cm,cs) or signature(m,s)!=signature(bm,bs):raise ValueError('evaluation data/decoder/scorer differs')
            setting='steps25_cfg2';paired={};untouched={}
            for metric in METRICS:
                ours=means_by_target(s['records'],setting,metric)
                paired[metric]=paired_comparison(means_by_target(cs['records'],setting,metric),ours,clusters=clusters)
                untouched[metric]=paired_comparison(means_by_target(bs['records'],setting,metric),ours,clusters=clusters)
            geometry={field:paired_comparison(geometry_by_target(cs['records'],field),geometry_by_target(s['records'],field),clusters=clusters)
                for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
            tm=paired['tm_fixed_reference'];base=untouched['tm_fixed_reference']
            passed=tm['theirs_minus_ours']>=.002 and base['theirs_minus_ours']>=0
            row=dict(task=task,paired=paired,vs_untouched=untouched,geometry=geometry,recovery_screen_passed=passed,
                training_seconds=t['training_seconds'],peak_reserved_gib=t['peak_reserved_bytes']/2**30)
            try:row['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),t['batches'],prefix='train::')
            except Exception as error:row['hardware']=dict(status='unavailable',error=str(error))
            result['runs'][run.name]=row
            lines.append(f"| {task['name']} | {task['seed']} | {tm['theirs']:.5f} | {tm['theirs_minus_ours']:+.5f} {tm['ci95']} | {base['theirs_minus_ours']:+.5f} | {passed} |")
        except Exception as error:result['failures'].append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
    if result['failures']:result['status']='incomplete'
    lines+=['','A successful screen requires at least +0.002 TM over its training control and recovery to the untouched checkpoint mean, followed by two more training seeds. It does not establish the +0.01 accuracy promotion rule. Geometry uses the inherited reference-short adjacency proxy.','',
        '```json',json.dumps(result,indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
