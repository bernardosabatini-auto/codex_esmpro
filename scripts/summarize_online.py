import argparse,json
from pathlib import Path
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores,means_by_target,hardware
from summarize_pilot import geometry_by_target
p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
run=a.runs[0];path=run/'manifest.json'
m=json.loads(path.read_text()) if path.exists() else dict(status='failed',precision={},completed_predictions=0,
    error='The registered job ended before producing a collection manifest; consult its scheduler exit state.')
result=dict(status=m['status'],precision=m['precision'])
lines=['# Complete sequence-to-backbone pipeline','',f"Status: {m['status']}; predictions: {m['completed_predictions']}/1878.",
 'The inherited development input sequences can omit unresolved residues. This benchmark includes fresh ESMC computation but retains those inputs for comparability.']
if m['status']=='complete':
 s=json.loads((run/'scores.json').read_text());validate_scores(m,s);root=Path(__file__).resolve().parents[1]
 ref=json.loads((root/'runs/comparison_49414524_0/scores.json').read_text());clusters=json.loads((root/'runs/development_clusters/clusters.json').read_text())['clusters']
 if ref['usalign']!=s['usalign']:raise ValueError('scoring protocol differs')
 result['online_minus_cached']={metric:paired_comparison(means_by_target(ref['records'],'steps25_cfg2',metric),means_by_target(s['records'],'steps25_cfg2',metric),clusters=clusters) for metric in ('tm_fixed_reference','ca_lddt')}
 reference_rows=[r for r in ref['records'] if r['setting']=='steps25_cfg2']
 result['geometry_delta']={field:paired_comparison(geometry_by_target(reference_rows,field),geometry_by_target(s['records'],field),clusters=clusters) for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
 result['development_noninferiority_passed']=(all(v['ci95'][0]>=-.005 for v in result['online_minus_cached'].values()) and all(v['ci95'][1]<=.001 for v in result['geometry_delta'].values()))
 seconds=sum(r['seconds'] for r in m['batches']);result.update(seconds=seconds,proteins_per_second=626/seconds,predictions_per_second=1878/seconds,resident_parameters=m['resident_parameters'],peak_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/2**30,hardware=hardware(Path(str(run)+'_nsight.sqlite'),m['batches']))
 if m['config'].get('online_reference_run'):
  reference_path=Path(m['config']['online_reference_run']);rm=json.loads((reference_path/'manifest.json').read_text());rs=json.loads((reference_path/'scores.json').read_text());validate_scores(rm,rs)
  for key in ('checkpoint','decoder_checkpoint','dataset','embedding_artifacts','resident_parameters'):
   if m[key]!=rm[key]:raise ValueError('online comparison changed '+key)
  for key in ('seed','samples','batches','target_ids','flow_steps','guidance'):
   if m['config'][key]!=rm['config'][key]:raise ValueError('online comparison changed '+key)
  if m['timing_scope']!=rm['timing_scope'] or s['usalign']!=rs['usalign']:raise ValueError('online timing or scoring protocol changed')
  result['online_minus_full_precision']={metric:paired_comparison(means_by_target(rs['records'],'steps25_cfg2',metric),means_by_target(s['records'],'steps25_cfg2',metric),clusters=clusters) for metric in ('tm_fixed_reference','ca_lddt')}
  result['geometry_minus_full_precision']={field:paired_comparison(geometry_by_target(rs['records'],field),geometry_by_target(s['records'],field),clusters=clusters) for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
  result['speedup_vs_full_precision']=sum(row['seconds'] for row in rm['batches'])/seconds
  result['full_precision_noninferiority_passed']=(all(row['ci95'][0]>=-.005 for row in result['online_minus_full_precision'].values()) and all(row['ci95'][1]<=.001 for row in result['geometry_minus_full_precision'].values()))
  result['development_speed_gate_passed']=result['full_precision_noninferiority_passed'] and result['speedup_vs_full_precision']>=2
 lines+=['',m['timing_scope'],'','Final ESMC layer only, with three samples averaged per target. Embeddings are recomputed from input sequences. The external ESMFold2 run used one protein at a time, whereas this pipeline batches different proteins: these numbers are not a matched-batch latency or optimized-throughput speed ratio.','', '```json',json.dumps(result,indent=2),'```']
else:lines+=['',m.get('error','Incomplete; no performance claim.')]
a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
