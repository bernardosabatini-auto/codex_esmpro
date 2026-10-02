"""Retain ordinary capacity reporting and audit every within-condition bijection."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from summarize_overfit import main as capacity_summary


def audit(run):
 m=json.loads((run/'manifest.json').read_text());c=m['config'];recipe=json.loads(Path(c['coupling_protocol']).read_text())
 if sha(c['coupling_protocol'])!=c['coupling_protocol_sha256'] or c['conditional_coupling']['group_size']!=recipe['group_size']:raise ValueError('Changed coupling protocol')
 rows=m.get('coupling_updates',[])
 if m['status']!='complete':return dict(complete_updates=len(rows),arm=c['conditional_coupling']['arm'])
 if len(rows)!=c['updates'] or [r['step'] for r in rows]!=list(range(1,c['updates']+1)):raise ValueError('Missing coupling updates')
 arm=c['conditional_coupling']['arm'];group=c['conditional_coupling']['group_size'];costs=[]
 for r in rows:
  length=(128,256,384,512)[(r['step']-1)%4];n=c['batches'][str(length)];p=r['permutation']
  if sorted(p)!=list(range(n)) or any(i//group!=j//group for i,j in enumerate(p)) or r['groups']!=n//group or len(r['costs'])!=n//group:raise ValueError('Invalid within-protein bijection')
  if arm=='independent' and p!=list(range(n)):raise ValueError('Independent labels changed')
  for x in r['costs']:
   if any(not np.isfinite(x[k]) or x[k]<-1e-10 for k in ('independent','optimal','applied')) or x['optimal']>x['independent']+1e-10 or x['applied']!=x[arm]:raise ValueError('Invalid transport cost')
   costs.append(x)
  for key in ('ids_sha256','labels_sha256','noise_sha256','targets_sha256','times_sha256','dropout_sha256','flow_rng_sha256','global_rng_sha256'):
   if len(r[key])!=64:raise ValueError('Missing random-draw accounting')
 return dict(complete_updates=len(rows),arm=arm,groups=len(costs),mean_independent_cost=float(np.mean([r['independent'] for r in costs])),mean_optimal_cost=float(np.mean([r['optimal'] for r in costs])),mean_applied_cost=float(np.mean([r['applied'] for r in costs])))


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();capacity_summary();d=json.loads(a.output.with_suffix('.json').read_text())
 if (a.runs[0]/'manifest.json').exists():
  d['conditional_coupling']=audit(a.runs[0]);d['elapsed_seconds']=json.loads((a.runs[0]/'manifest.json').read_text()).get('elapsed_seconds')
 a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');s=a.output.with_suffix('.md').read_text().replace('Fresh32-sample ensembles at both CFG settings','Fresh32-sample ensembles at the configured guidance values');s+='\nWithin-sequence coupling audit:\n'+json.dumps(d.get('conditional_coupling',{}),indent=2)+'\n\nContiguous groups of8same-protein examples; target marginals preserved exactly. Compare only matched grouping/noise recipes; lower transport or training loss is not evidence of improved structural diversity.\n';a.output.with_suffix('.md').write_text(s)
if __name__=='__main__':main()
