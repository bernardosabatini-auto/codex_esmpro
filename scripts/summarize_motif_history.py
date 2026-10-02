"""Audit matched sampler histories and apply the frozen raw-quality gate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.fragment_designability import motif_error
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics


def analyze(run):
 if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest')
 m=json.loads((run/'manifest.json').read_text())
 if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),controls=m['controls'],completed_samples=len(m['records']))
 c=m['config']
 for key in ('protocol','parent_manifest','parent_predictions','selection','checkpoint','decoder_checkpoint'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 rows=json.loads(Path(c['selection']).read_text())['rows'];ids={r['target_id'] for r in rows};wanted={(i,k) for i in ids for k in range(4)}
 if len(rows)!=16 or len(m['records'])!=64 or {(r['target_id'],r['slot']) for r in m['records']}!=wanted:raise ValueError('Incomplete outputs')
 if len(m['controls'])!=16 or {(r['target_id'],r['slot']) for r in m['controls']}!={(i,k) for i in c['control_ids'] for k in range(4)}:raise ValueError('Incomplete baseline controls')
 if len(m['batches'])!=16 or {r['target_id'] for r in m['batches']}!=ids or any(r['velocity_evaluations']!=148 for r in m['batches']):raise ValueError('Changed compute budget')
 records=[]
 with h5py.File(run/'predictions.h5') as f,h5py.File(c['parent_predictions']) as parent:
  for row in rows:
   ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;keep=np.zeros(n,bool);keep[st:st+k]=True;ref=np.zeros((n,4,3),np.float32);ref[st:st+k]=parent[ident+'/fragment'][:]
   if ident in c['control_ids']:
    for slot in range(4):
     bb=f[ident+'/baseline_control'][slot];original=parent[ident+'/backbone'][slot];actual=ca_metrics(bb[:,1],original[:,1]);dz=float(np.max(abs(f[ident+'/baseline_control_latent'][slot]-parent[ident+'/latent'][slot])))
     if dz>1e-5 or actual['ca_rmsd']>.2 or actual['ca_lddt']<.99 or bool(backbone_geometry(bb[None])['coarse_valid'][0])!=bool(backbone_geometry(original[None])['coarse_valid'][0]):raise ValueError('Baseline control failed independent audit')
   for mode,bb in [('outer_only',parent[ident+'/backbone'][:]),('each_evaluation',f[ident+'/backbone'][:])]:
    if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all():raise ValueError('Invalid backbone array')
    errors=motif_error(bb,ref,keep);valid=backbone_geometry(bb)['coarse_valid']
    for slot in range(4):
     if mode=='each_evaluation':
      saved=next(r for r in m['records'] if (r['target_id'],r['slot'])==(ident,slot))
      if abs(saved['motif_drms']-errors[slot])>1e-5 or saved['coarse_valid']!=bool(valid[slot]):raise ValueError('Stored outcome audit failed')
     records.append(dict(mode=mode,target_id=ident,family=row['family'],slot=slot,motif_drms=float(errors[slot]),coarse_valid=bool(valid[slot]),motif_success=bool(errors[slot]<=1),joint_success=bool(valid[slot] and errors[slot]<=1)))
 summaries=[]
 for mode in ('outer_only','each_evaluation'):
  rr=[r for r in records if r['mode']==mode];summaries.append(dict(mode=mode,n=len(rr),**{key:float(np.mean([r[key] for r in rr])) for key in ('motif_drms','coarse_valid','motif_success','joint_success')}))
 differences=[];rng=np.random.default_rng(2026100219);ix=rng.integers(0,16,(10000,16))
 for key in ('motif_drms','coarse_valid','motif_success','joint_success'):
  delta=np.array([np.mean([r[key] for r in records if r['target_id']==i and r['mode']=='each_evaluation'])-np.mean([r[key] for r in records if r['target_id']==i and r['mode']=='outer_only']) for i in sorted(ids)]);differences.append(dict(metric=key,delta=float(delta.mean()),family_interval=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
 qualified=next(r for r in differences if r['metric']=='joint_success')['family_interval'][0]>0 and summaries[1]['motif_success']>=.98 and summaries[1]['motif_drms']-summaries[0]['motif_drms']<=.1
 return dict(status='complete',summaries=summaries,differences=differences,records=records,controls=m['controls'],generation_seconds=sum(r['seconds'] for r in m['batches']),elapsed_seconds=m['elapsed_seconds'],peak_GiB=max(r['peak_reserved_bytes'] for r in m['batches'])/2**30,qualified_for_refolding=bool(qualified),designability_tested=False)


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Inner refinement self-conditioning','',f"Status: {d['status']}."]
 if d['status']=='complete':
  lines+=['','All16families/four seeds. Same isolated-fragment codes,noises,weights,times,decoder and148velocity evaluations per sample. Only update cadence differs.16saved baseline controls independently audited.','', '| History refresh | Motif dRMS A | Motif <=1A | Coarse valid | Joint |','|---|---:|---:|---:|---:|']
  for r in d['summaries']:lines.append(f"| {r['mode']} | {r['motif_drms']:.3f} | {r['motif_success']:.3f} | {r['coarse_valid']:.3f} | {r['joint_success']:.3f} |")
  for r in d['differences']:lines.append(f"- Each evaluation minus outer-only {r['metric']}: {r['delta']:+.4f},95%family interval {r['family_interval']}.")
  lines += ['',f"Qualified for fixed-sequence design/refolding: {d['qualified_for_refolding']}. Generation {d['generation_seconds']:.2f}s,peak reserved{d['peak_GiB']:.2f}GiB.",'','No designability, independent-test or experimental claim; all failures retained. No model parameters trained.']
 else:lines+=['',d['error']]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
