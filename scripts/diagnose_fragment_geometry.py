"""CPU localization of fragment-scaffold failures and existing random motif coverage."""
import json
from pathlib import Path
import h5py,numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_error
from prepare_overfit import sha

root=Path(__file__).resolve().parents[1];isolated=root/'runs/isolated_motif_49864561';parent=root/'runs/generative_pilot_49855378';noise=root/'runs/noise_guidance_49863415';rows=json.loads((root/'runs/generative_pilot_selection.json').read_text())['rows'];records=[];random=[]
with h5py.File(isolated/'predictions.h5') as iso,h5py.File(parent/'predictions.h5') as old,h5py.File(noise/'predictions.h5') as draws:
 for r in rows:
  ident=r['target_id'];n=r['length'];k=max(8,int(.3*n));st=(n-k)//2;positions=np.arange(n-1);regions={'motif_internal':(positions>=st)&(positions<st+k-1),'boundary':(positions==st-1)|(positions==st+k-1),'scaffold_internal':(positions<st-1)|(positions>=st+k)}
  for mode,bb in [('isolated',iso[ident+'/backbone'][:]),('full_context',old['original50/motif_u3/'+ident+'/backbone'][:])]:
   geometry=backbone_geometry(bb);d=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1);bad=(d<1.1)|(d>1.6);gap=np.linalg.norm(np.diff(bb[:,:,1],axis=1),axis=-1)>4.5;ca=bb[:,:,1];dist=np.linalg.norm(ca[:,:,None]-ca[:,None,:],axis=-1);ii,jj=np.triu_indices(n,3);clash=dist[:,ii,jj]<2.5;inside=(np.arange(n)>=st)&(np.arange(n)<st+k);clash_regions={'motif_internal':inside[ii]&inside[jj],'motif_scaffold':inside[ii]^inside[jj],'scaffold_internal':~inside[ii]&~inside[jj]}
   for slot in range(4):records.append(dict(target_id=ident,mode=mode,slot=slot,**{key:float(v[slot]) for key,v in geometry.items()},gap_region_counts={key:int(gap[slot,mask].sum()) for key,mask in regions.items()},clash_region_counts={key:int(clash[slot,mask].sum()) for key,mask in clash_regions.items()},peptide_region_counts={key:int(bad[slot,mask].sum()) for key,mask in regions.items()},region_sizes={key:int(mask.sum()) for key,mask in regions.items()}))
  if ident in draws:
   keep=np.zeros(n,bool);keep[st:st+k]=True;ref=np.zeros((n,4,3),np.float32);ref[st:st+k]=iso[ident+'/fragment'][:]
   for slot in range(2):
    bb=draws[f'{ident}/{slot}/random_all'][:];errors=motif_error(bb,ref,keep);best=int(errors.argmin());random.append(dict(target_id=ident,slot=slot,best_index=best,best_motif_drms=float(errors[best]),count_under1A=int((errors<=1).sum()),draws=len(errors)))
summary=[]
for mode in ('full_context','isolated'):
 rr=[r for r in records if r['mode']==mode];summary.append(dict(mode=mode,n=len(rr),peptide_failed=sum(r['peptide_outlier_fraction']>.05 for r in rr),clash_failed=sum(r['ca_clashing_residue_fraction']>.01 for r in rr),gap_failed=sum(r['ca_gap_fraction']>.01 for r in rr),gap_region_counts={key:sum(r['gap_region_counts'][key] for r in rr) for key in rr[0]['region_sizes']},clash_region_counts={key:sum(r['clash_region_counts'][key] for r in rr) for key in rr[0]['clash_region_counts']},region_outlier_rates={key:sum(r['peptide_region_counts'][key] for r in rr)/sum(r['region_sizes'][key] for r in rr) for key in rr[0]['region_sizes']}))
d=dict(sources={str(p):sha(p) for p in (isolated/'predictions.h5',parent/'predictions.h5',noise/'predictions.h5')},summary=summary,records=records,random_motif_diagnostic=random)
(root/'reports/fragment_failure_diagnostic_20261002.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Isolated-fragment failure localization','','CPU development diagnostic; no new sampling, selection for promotion or thresholds.',json.dumps(summary,indent=2),'','Motif retention among the existing33random draws per fixed case (exploratory selection using supplied fragment only):',json.dumps(random,indent=2)]
(root/'reports/fragment_failure_diagnostic_20261002.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(summary=summary,random=random),indent=2))
