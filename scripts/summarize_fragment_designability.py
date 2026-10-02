"""Full audit of isolated-fragment designability and joint motif preservation."""
import argparse,json
from pathlib import Path
from itertools import combinations
import h5py,numpy as np
from prepare_fragment_designability import audit_inputs
from summarize_designability import analyze as design_audit
from summarize_isolated_motif import analyze as generation_audit
from latentfold.metrics import usalign_coordinates


def analyze(run):
 if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest')
 m=json.loads((run/'manifest.json').read_text())
 if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
 c=m['config'];audit_inputs(c);d=design_audit(run);generation=generation_audit(Path(c['generation_manifest']).parent)
 if generation['status']!='complete' or len(d['backbones'])!=20 or d['completed_refolds']!=160:raise ValueError('Incomplete assay')
 controls=[r for r in d['backbones'] if r['head']=='experimental']
 if len(controls)!=4 or not all(r['valid_designable'] for r in controls):raise ValueError('Experimental positive-control failure')
 for r in d['backbones']:
  if r['mode']!='real':
   parent=next(x for x in generation['records'] if (x['mode'],x['target_id'],x['slot'])==(r['mode'],r['target_id'],r['slot']))
   if abs(parent['motif_drms']-r['motif_drms'])>1e-7:raise ValueError('Motif score changed')
 summaries=[];diversity=[]
 with h5py.File(c['predictions']) as f:
  bbs={r['name']:f[r['dataset']][:] if r['head']=='experimental' else f[r['dataset']][r['slot']] for r in d['backbones']}
  for mode in ('full_context','isolated'):
   rr=[r for r in d['backbones'] if r['mode']==mode];summaries.append(dict(mode=mode,n=len(rr),**{key:float(np.mean([r[key] for r in rr])) for key in ('motif_drms','coarse_valid','designable','valid_designable','joint_motif_success','valid_joint_motif_success','sc_tm')}))
   for scope in ('all','valid_designable','valid_joint_motif_success'):
    pairs=[]
    for family in sorted({r['family'] for r in rr}):
     eligible=[r for r in rr if r['family']==family and (scope=='all' or r[scope])]
     for x,y in combinations(eligible,2):pairs.append(dict(family=family,tm=usalign_coordinates(c['usalign'],bbs[x['name']][:,1],bbs[y['name']][:,1])))
    diversity.append(dict(mode=mode,scope=scope,pairs=pairs,mean_pairwise_tm=float(np.mean([r['tm'] for r in pairs])) if pairs else None))
 return dict(status='complete',summaries=summaries,diversity=diversity,backbones=d['backbones'],completed_refolds=160,controls=controls,mpnn_seconds=d['mpnn_seconds'],assay_elapsed_seconds=d['elapsed_seconds'])


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Isolated-fragment scaffolding designability','',f"Status: {d['status']}."]
 if d['status']=='complete':
  lines+=['','All8fixed samples per method plus4experimental controls;160refolds audited. All positive and repeatability controls passed. Joint requires motif dRMS<=1A, full-backbone validity and best8scTM>.5.','', '| Codes | Motif dRMS A | Geometry | Designable | Joint |','|---|---:|---:|---:|---:|']
  for r in d['summaries']:lines.append(f"| {r['mode']} | {r['motif_drms']:.3f} | {r['coarse_valid']:.3f} | {r['designable']:.3f} | {r['valid_joint_motif_success']:.3f} |")
  lines+=['','Pairwise diversity with pair counts:']
  for r in d['diversity']:lines.append(f"- {r['mode']} {r['scope']}: {len(r['pairs'])} pairs,mean fixed-correspondence TM {r['mean_pairwise_tm']}.")
  lines+=['',f"MPNN {d['mpnn_seconds']:.2f}s; assay elapsed {d['assay_elapsed_seconds']:.2f}s.",'','Four-family profile only; sparse successful pairs do not establish ensemble capacity. Separate sequence designs do not establish one-sequence multistability. No experimental validation, independent-test or end-to-end speed claim.']
 else:lines+=['',d['error']]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
