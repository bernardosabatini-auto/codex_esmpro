import argparse,json
from pathlib import Path
from latentfold.metrics import paired_comparison
from summarize_comparison import hardware,means_by_target,validate_scores
p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
run=a.runs[0];d=json.loads((run/'manifest.json').read_text());result=dict(status=d['status'])
lines=['# ESMFold2-Fast fixed-correspondence benchmark','',f"Status: {d['status']}; {d['completed_predictions']}/1878 predictions."]
if d['status']=='complete':
 scores=json.loads((run/'scores.json').read_text());keys=[(r['target_id'],r['sample']) for r in scores['records']]
 if len(keys)!=1878 or set(keys)!={(n,k) for n in d['target_ids'] for k in range(3)}:raise ValueError('external score coverage failure')
 root=Path(__file__).resolve().parents[1];ref=root/'runs/comparison_49414524_0';rm=json.loads((ref/'manifest.json').read_text());rs=json.loads((ref/'scores.json').read_text());validate_scores(rm,rs)
 clusters=json.loads((root/'runs/development_clusters/clusters.json').read_text())['clusters']
 result['external_minus_pair']={m:paired_comparison(means_by_target(rs['records'],'steps25_cfg2',m),means_by_target(scores['records'],'esmfold2_steps50_loops3',m),clusters=clusters) for m in ('tm_fixed_reference','ca_lddt')}
 result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),d['batches'])
 seconds=sum(r['seconds'] for r in d['batches']);result['proteins_per_second']=626/seconds;result['predictions_per_second']=1878/seconds
 lines+=['','All three samples are retained and averaged per target; no confidence or oracle selection. Three trunk loops and 50 diffusion steps, strict FP32.','',
 'ESMFold2 timings include sequence conditioning and confidence prediction. The pair-head reference timings exclude ESMC, so these timings do not establish an end-to-end speed ratio.','',
 'External minus untouched pair reference:','```json',json.dumps(result,indent=2),'```']
else:lines+=['',d.get('error','Incomplete; no benchmark conclusion.')]
a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
