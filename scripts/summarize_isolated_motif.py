"""Audit fragment-only scaffolding against archived full-context outputs."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.fragment_designability import motif_error
from generate_isolated_motif import canonical_fragment
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
 if len(m['records'])!=64 or {(r['target_id'],r['slot']) for r in m['records']}!=wanted or len(m['fragments'])!=16 or {r['target_id'] for r in m['fragments']}!=ids:raise ValueError('Incomplete generation')
 poses=[r for r in m['controls'] if r['kind']=='fragment_pose'];full=[r for r in m['controls'] if r['kind']=='full_context']
 if len(poses)!=16 or {r['target_id'] for r in poses}!=ids or any(r['coordinate_max_abs']>1e-4 or r['latent_rmse']>1e-4 for r in poses):raise ValueError('Fragment pose controls failed')
 if len(full)!=16 or {(r['target_id'],r['slot']) for r in full}!={(i,k) for i in c['control_ids'] for k in range(4)} or any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in full):raise ValueError('Full context controls failed')
 records=[];diversity=[]
 with h5py.File(run/'predictions.h5') as f,h5py.File(c['parent_predictions']) as parent:
  for row in rows:
   ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;keep=np.zeros(n,bool);keep[st:st+k]=True;ref=np.zeros((n,4,3),np.float32);expected,_=canonical_fragment(np.asarray(row['reference']['backbone'],np.float32)[st:st+k]);fragment=f[ident+'/fragment'][:]
   if not np.array_equal(fragment,expected):raise ValueError('Fragment preparation changed')
   ref[st:st+k]=fragment;rt=f[ident+'/fragment_roundtrip'][:];rr=next(r for r in m['fragments'] if r['target_id']==ident)
   if abs(float(motif_error(rt[None],fragment,np.ones(k,bool))[0])-rr['roundtrip_drms'])>1e-5:raise ValueError('Roundtrip score audit failed')
   for mode,bb in [('isolated',f[ident+'/backbone'][:]),('full_context',parent['original50/motif_u3/'+ident+'/backbone'][:])]:
    if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all():raise ValueError('Invalid backbone array')
    errors=motif_error(bb,ref,keep);valid=backbone_geometry(bb)['coarse_valid']
    for slot in range(4):
     if mode=='isolated':
      saved=next(r for r in m['records'] if (r['target_id'],r['slot'])==(ident,slot))
      if abs(saved['motif_drms']-errors[slot])>1e-5 or saved['coarse_valid']!=bool(valid[slot]):raise ValueError('Outcome audit failed')
     records.append(dict(mode=mode,target_id=ident,family=row['family'],slot=slot,motif_drms=float(errors[slot]),coarse_valid=bool(valid[slot]),motif_success=bool(errors[slot]<=1),joint_success=bool(valid[slot] and errors[slot]<=1)))
    for i in range(4):
     for j in range(i+1,4):diversity.append(dict(mode=mode,target_id=ident,slots=[i,j],**ca_metrics(bb[i,:,1],bb[j,:,1])))
 summaries=[]
 for mode in ('full_context','isolated'):
  rr=[r for r in records if r['mode']==mode];summaries.append(dict(mode=mode,n=len(rr),**{key:float(np.mean([r[key] for r in rr])) for key in ('motif_drms','coarse_valid','motif_success','joint_success')}))
 differences=[];rng=np.random.default_rng(2026100218);ix=rng.integers(0,16,(10000,16))
 for key in ('motif_drms','coarse_valid','motif_success','joint_success'):
  delta=np.array([np.mean([r[key] for r in records if r['target_id']==i and r['mode']=='isolated'])-np.mean([r[key] for r in records if r['target_id']==i and r['mode']=='full_context']) for i in sorted(ids)]);differences.append(dict(metric=key,delta=float(delta.mean()),family_interval=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
 return dict(status='complete',summaries=summaries,differences=differences,fragments=m['fragments'],records=records,diversity=diversity,controls=m['controls'],generation_seconds=sum(r['seconds'] for r in m['batches']),elapsed_seconds=m['elapsed_seconds'],peak_GiB=max(r['peak_reserved_bytes'] for r in m['batches'])/2**30,designability_tested=False)


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Isolated-fragment motif scaffolding','',f"Status: {d['status']}."]
 if d['status']=='complete':
  lines+=['','All16fixed families/four seeds retained. Same original50/AE3/RePaint3 recipe and noise streams. Isolated fragments supply their own frame and encoder input.','', '| Codes | Motif dRMS A | Motif <=1A | Coarse valid | Joint |','|---|---:|---:|---:|---:|']
  for r in d['summaries']:lines.append(f"| {r['mode']} | {r['motif_drms']:.3f} | {r['motif_success']:.3f} | {r['coarse_valid']:.3f} | {r['joint_success']:.3f} |")
  for r in d['differences']:lines.append(f"- Isolated minus full-context {r['metric']}: {r['delta']:+.4f},95%family interval {r['family_interval']}.")
  lines += ['',f"Standalone fragment roundtrip mean dRMS {np.mean([r['roundtrip_drms'] for r in d['fragments']]):.3f}A. Generation {d['generation_seconds']:.2f}s, peak reserved {d['peak_GiB']:.2f}GiB.",'','This practical comparison changes scaffold context, canonical frame and encoder positions; it does not isolate their causal contributions. Geometry and motif retention do not establish designability. No test structures used.']
 else:lines+=['',d['error']]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
