"""Summarize reference-only NMR control screening, before model predictions."""
import argparse,json
from collections import Counter
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
m=json.loads((a.runs[0]/'screen.json').read_text())
summary=dict(status=m['status'],accepted_candidates=len(m['accepted']),rejected_candidates=len(m['rejected']),protocol=m.get('protocol'),rejections=dict(Counter(r['reason'].split(':')[0] for r in m['rejected'])),scope='Reference candidates only; family separation and final panel selection still required')
if m.get('error'):summary['error']=m['error']
a.output.with_suffix('.json').write_text(json.dumps(summary,indent=2)+'\n')
a.output.with_suffix('.md').write_text('# Experimental low-dispersion control screening\n\n'+f"Status: {summary['status']}. Accepted candidates: {summary['accepted_candidates']}; rejected: {summary['rejected_candidates']}.\n\n"+'At least ten experimental models; up to sixteen evenly spaced models evaluated. Mean pairwise CA RMSD <=1 A, 90th percentile <=1.5 A, and at least 95% common complete-backbone coverage. These are low experimental-model dispersion controls, not evidence of equilibrium populations or dynamical rigidity. No generated model predictions enter selection. Family separation and final panel selection remain required.\n')
