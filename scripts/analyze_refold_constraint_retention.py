"""Exploratory stricter design test: the same refold must retain the constraint."""
import json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_error
from summarize_noise_guidance import contact


def analyze(run,kind,report):
 m=json.loads((run/'manifest.json').read_text());d=report if isinstance(report,dict) else json.loads(report.read_text())
 if m['status']!='complete' or d['status']!='complete':raise ValueError('Complete audited assay required')
 if d['completed_refolds']!=len(m['records']):raise ValueError('Incomplete assay')
 results=[];refs=Path(m['config']['reference_predictions']);sources={str(p):sha(p) for p in (run/'manifest.json',run/'refolded.h5',refs,*(() if isinstance(report,dict) else (report,)))}
 with h5py.File(run/'refolded.h5') as f,h5py.File(refs) as reference:
  for r in d['backbones']:
   if r['head']=='experimental':continue
   records=sorted([x for x in m['records'] if x['name']==r['name']],key=lambda x:x['sequence_index'])
   if len(records)!=8:raise ValueError('Missing refolds')
   bb=np.stack([f[r['name']+'/'+str(x['sequence_index'])][:] for x in records]);valid=backbone_geometry(bb)['coarse_valid']
   if kind=='contact':errors=np.abs(contact(bb)-8);raw_joint=r['joint_success']
   else:
    n=r['length'];k=max(8,int(.3*n));st=(n-k)//2;keep=np.zeros(n,bool);keep[st:st+k]=True;errors=motif_error(bb,reference['references/'+r['target_id']+'/backbone'][:],keep);raw_joint=r['valid_joint_motif_success']
   tm=np.array([x['sc_tm'] for x in records]);same_sequence=(tm>.5)&valid&(errors<=1)
   results.append(dict(name=r['name'],target_id=r['target_id'],slot=r['slot'],mode=r['mode'],original_joint_success=bool(raw_joint),same_sequence_constraint_designable=bool(same_sequence.any()),strict_joint_success=bool(raw_joint and same_sequence.any()),successful_refold_indices=[records[i]['sequence_index'] for i in np.flatnonzero(same_sequence)],refold_constraint_errors=errors.tolist(),refold_coarse_valid=valid.tolist(),refold_sc_tm=tm.tolist()))
 summaries=[]
 for mode in sorted({r['mode'] for r in results}):
  rr=[r for r in results if r['mode']==mode];summaries.append(dict(mode=mode,n=len(rr),original_joint=sum(r['original_joint_success'] for r in rr),strict_joint=sum(r['strict_joint_success'] for r in rr),any_refold_constraint_designable=sum(r['same_sequence_constraint_designable'] for r in rr)))
 return dict(kind=kind,sources=sources,summaries=summaries,backbones=results)


def main():
 root=Path(__file__).resolve().parents[1];rows=[analyze(root/'runs/noise_designability_49863726','contact',root/'reports/noise_designability_49863726.json'),analyze(root/'runs/fragment_designability_49865077','motif',root/'reports/fragment_designability_49865077.json')];out=root/'reports/refold_constraint_retention_20261002';out.with_suffix('.json').write_text(json.dumps(rows,indent=2)+'\n');lines=['# Constraint retention after sequence design and refolding','','Exploratory stricter CPU analysis of existing complete assays; no new GPU sampling or thresholds tuned. Requires the same one of8designed sequences to have refold scTM>.5, valid full-backbone geometry and contact error/motif dRMS<=1A. Strict joint additionally retains the original generated-backbone joint gate; no failed raw output is rescued.','']
 for d in rows:lines += [d['kind'],json.dumps(d['summaries'],indent=2),'']
 lines+=['Four-family feasibility panels only; this still does not establish experimental function or one-sequence multistability.'];out.with_suffix('.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
