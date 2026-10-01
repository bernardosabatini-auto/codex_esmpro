"""Validate paired training draws and compare full-sampling development accuracy."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores,means_by_target,hardware

METRICS=('tm_fixed_reference','ca_lddt')

def validate_training_evaluation(training,manifest,scores):
 validate_scores(manifest,scores)
 cfg=manifest['config']
 if any(cfg[k]!=v for k,v in dict(flow_steps=[25],guidance=[2],samples=3,decoder_steps=3).items()):
  raise ValueError('training evaluation sampling differs from declared protocol')
 if manifest['checkpoint']['sha256']!=training['checkpoint_sha256']:
  raise ValueError('evaluation did not use the recorded trained weights')
 if manifest['decoder_checkpoint']['sha256']!=training['config']['decoder_checkpoint_sha256']:
  raise ValueError('evaluation decoder changed')
 if manifest['precision']!={'flow_precision':'fp32','decoder_precision':'fp32'}:
  raise ValueError('training evaluation must use strict FP32')
 if scores['usalign']['arguments']!=['-TMscore','1']:
  raise ValueError('evaluation correspondence protocol changed')

def geometry_by_target(records,field):
 if len({r['setting'] for r in records})!=1:raise ValueError('geometry comparison requires exactly one sampling setting')
 groups={}
 for row in records:groups.setdefault(row['target_id'],[]).append(row[field]/max(1,row['reference_adjacent_short_count']))
 return {k:float(np.mean(v)) for k,v in groups.items()}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 groups={};failures=[];result=dict(status='running',seeds={},runs={},hardware_warnings=[])
 for run in a.runs:
  try:
   training=json.loads((run/'training.json').read_text());manifest=json.loads((run/'evaluation/manifest.json').read_text())
   if manifest['status']!='complete':raise ValueError(manifest.get('error','incomplete evaluation'))
   scores=json.loads((run/'evaluation/scores.json').read_text())
   validate_training_evaluation(training,manifest,scores)
   if training['status']!='complete' or training['steps']!=training['config']['updates']:raise ValueError('incomplete training')
   if any(r['aux_to_flow_ratio']>.100001 for r in training['rows']):raise ValueError('auxiliary gradient exceeded cap')
   task=training['task'];key=(task['seed'],task['arm'])
   if key in groups:raise ValueError('duplicate seed/arm')
   trace=Path(str(run)+'_nsight.sqlite')
   groups[key]=dict(training=training,records=scores['records'],evaluation_signature=(manifest['dataset'],manifest['decoder_checkpoint'],manifest['precision'],scores['usalign']))
   result['runs'][run.name]=dict(task=task,training_seconds=training['training_seconds'],peak_reserved_gib=training['peak_reserved_bytes']/2**30)
   for label,batches,prefix in [('training_hardware',training['batches'],'train::'),('evaluation_hardware',manifest['batches'],'collect::')]:
    try:result['runs'][run.name][label]=hardware(trace,batches,prefix=prefix)
    except Exception as error:
     result['hardware_warnings'].append(dict(run=str(run),stage=label,error=f'{type(error).__name__}: {error}'))
     result['runs'][run.name][label]=dict(status='unavailable',reason=str(error))
  except Exception as error:failures.append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
 if failures:
  result.update(status='incomplete',failures=failures,development_gate_passed=False)
  lines=['# Matched training pilot','', 'Incomplete; no accuracy promotion.',*['- '+r['run']+': '+r['error'] for r in failures]]
  # Preserve useful completed evidence without treating missing seeds as successes.
  result['available_seed_diagnostics']={}
  for seed in sorted({key[0] for key in groups}):
   if (seed,'flow') not in groups or (seed,'geometry') not in groups:continue
   config=groups[seed,'flow']['training']['config']
   cluster_path=Path(config['development_clusters'])
   if hashlib.sha256(cluster_path.read_bytes()).hexdigest()!=config['development_clusters_sha256']:raise ValueError('development clusters changed')
   clusters=json.loads(cluster_path.read_text())['clusters']
   control=groups[seed,'flow'];geometry=groups[seed,'geometry']
   if control['evaluation_signature']!=geometry['evaluation_signature']:raise ValueError('paired evaluation data or scoring implementation differs')
   signature=lambda g:[(r['step'],r['bucket'],r['batch'],r['flow_rng_sha256'],r['input_ids_sha256']) for r in g['training']['rows']]
   if signature(control)!=signature(geometry):raise ValueError('paired inputs or stochastic draws differed')
   paired={m:paired_comparison(means_by_target(control['records'],'steps25_cfg2',m),means_by_target(geometry['records'],'steps25_cfg2',m),clusters=clusters) for m in METRICS}
   result['available_seed_diagnostics'][str(seed)]=paired
   tm=paired['tm_fixed_reference'];lines+=['',f"Available seed {seed}: control TM {tm['ours']:.5f}, geometry TM {tm['theirs']:.5f}, paired difference {tm['theirs_minus_ours']:+.5f}, cluster CI {tm['ci95']}. This does not replace the missing replication."]
  if any(v['tm_fixed_reference']['theirs_minus_ours']<=0 for v in result['available_seed_diagnostics'].values()):
   result['decision']='Stop this geometry recipe: available nonpositive seeds already violate the all-seeds-positive promotion rule. Preserve the failed stability control; no accuracy promotion or additional scale-up.'
   lines+=['',result['decision']]
  lines+=['','GPU hardware for completed evaluations:','```json',json.dumps(result['runs'],indent=2),'```']
 else:
  config=next(iter(groups.values()))['training']['config']
  if any(g['training']['config']!=config for g in groups.values()):raise ValueError('training protocols differ')
  if set(groups)!={(t['seed'],t['arm']) for t in config['tasks']}:raise ValueError('task coverage differs')
  cluster_path=Path(config['development_clusters'])
  if hashlib.sha256(cluster_path.read_bytes()).hexdigest()!=config['development_clusters_sha256']:raise ValueError('development clusters changed')
  cluster_data=json.loads(cluster_path.read_text());clusters=cluster_data['clusters']
  baseline=Path(config['reference_run']);bm=json.loads((baseline/'manifest.json').read_text());bs=json.loads((baseline/'scores.json').read_text());validate_scores(bm,bs)
  baseline_signature=(bm['dataset'],bm['decoder_checkpoint'],bm['precision'],bs['usalign'])
  if any(g['evaluation_signature']!=baseline_signature for g in groups.values()):raise ValueError('evaluation data or scoring implementation differs from untouched reference')
  setting='steps25_cfg2';baseline_scores={m:means_by_target(bs['records'],setting,m) for m in METRICS}
  lines=['# Matched training pilot','',f"{config['updates']} updates; {len(config['tasks'])} jobs; fixed 1,024-protein training subset. Full 25-step/guidance-2 sampling, three fixed samples averaged per development protein. No oracle selection.",'',
     'This is a small continued-training pilot. The 626 proteins are reused development data; scores from the locked final test are not used here.','',
     f"Uncertainty: paired sequence-cluster bootstrap across {cluster_data['n_clusters']} operational clusters. Inference samples are repeated measurements, not independent proteins.",'',
     '| Training seed | Control mean TM | Geometry mean TM | Difference [95% cluster CI] | Control vs untouched |','|---:|---:|---:|---|---:|']
  aggregate={arm:{m:{} for m in METRICS} for arm in ('flow','geometry')}
  for seed in sorted({key[0] for key in groups}):
   control=groups[seed,'flow'];geometry=groups[seed,'geometry']
   signature=lambda g:[(r['step'],r['bucket'],r['batch'],r['flow_rng_sha256'],r['input_ids_sha256']) for r in g['training']['rows']]
   if signature(control)!=signature(geometry):raise ValueError('paired training inputs or stochastic draws differed')
   paired={}
   for metric in METRICS:
    means={arm:means_by_target(groups[seed,arm]['records'],setting,metric) for arm in ('flow','geometry')}
    paired[metric]=paired_comparison(means['flow'],means['geometry'],clusters=clusters)
    paired['flow_vs_untouched_'+metric]=paired_comparison(baseline_scores[metric],means['flow'],clusters=clusters)
    for arm in means:
     for name,value in means[arm].items():aggregate[arm][metric].setdefault(name,[]).append(value)
   paired['geometry']={field:paired_comparison(geometry_by_target(control['records'],field),geometry_by_target(geometry['records'],field),clusters=clusters) for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
   result['seeds'][str(seed)]=paired;tm=paired['tm_fixed_reference'];ci=tm['ci95']
   lines.append(f"| {seed} | {tm['ours']:.5f} | {tm['theirs']:.5f} | {tm['theirs_minus_ours']:+.5f} [{ci[0]:+.5f}, {ci[1]:+.5f}] | {paired['flow_vs_untouched_tm_fixed_reference']['theirs_minus_ours']:+.5f} |")
  result['mean_across_training_seeds']={metric:paired_comparison({k:float(np.mean(v)) for k,v in aggregate['flow'][metric].items()}, {k:float(np.mean(v)) for k,v in aggregate['geometry'][metric].items()},clusters=clusters) for metric in METRICS}
  tm=result['mean_across_training_seeds']['tm_fixed_reference'];lddt=result['mean_across_training_seeds']['ca_lddt']
  accuracy=tm['theirs_minus_ours']>=.01 and tm['ci95'][0]>0 and len(result['seeds'])>=3 and all(v['tm_fixed_reference']['theirs_minus_ours']>0 for v in result['seeds'].values())
  geometry_ok=all(m['ci95'][1]<=.001 for v in result['seeds'].values() for m in v['geometry'].values())
  result.update(status='complete',development_gate_passed=accuracy and lddt['ci95'][0]>=-.005 and geometry_ok)
  lines+=['',f"Mean across training seeds: TM difference {tm['theirs_minus_ours']:+.5f}, cluster CI {tm['ci95']}. This CI averages the observed training seeds; it is not a well-powered estimate of training-seed uncertainty.",
      f"Development promotion gate: {result['development_gate_passed']}. Confirmation on the locked final test remains required for any accuracy claim.",'',
      'Geometry checks here use the inherited reference-short adjacency proxy because the development cache lacks original residue maps. Training and the new final test have explicit maps.','',
      'GPU hardware and memory:','```json',json.dumps(result['runs'],indent=2),'```']
 if result['hardware_warnings']:lines+=['','Some profiler intervals have missing counters; those hardware measurements are unavailable. This does not remove valid structure scores.','```json',json.dumps(result['hardware_warnings'],indent=2),'```']
 a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
