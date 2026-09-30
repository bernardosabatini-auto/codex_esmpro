"""CPU diagnostic of the inherited PCA/skewness frame on verified training data."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import h5py,numpy as np


def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 path=a.source/'code/canonicalize.py'
 spec=importlib.util.spec_from_file_location('audited_canonicalize',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 rows=[]
 with h5py.File(a.dataset,'r') as h:
  for name in h['train']:
   ca=h['train'][name]['ca_coords'][:];base,rot,info=module.canonicalize_coords(ca)
   seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'little');rng=np.random.default_rng(seed)
   q,_=np.linalg.qr(rng.normal(size=(3,3)));q[:,0]*=np.linalg.det(q)
   rigid,_,_=module.canonicalize_coords((ca@q+10).astype(np.float32))
   row=dict(id=name,length=len(ca),rigid_frame_rmsd=float(np.sqrt(((rigid-base)**2).sum(1).mean())),eigenvalue_ratios=info['ev_ratios'],perturbations=[])
   centered=base-base.mean(0);row['min_abs_skew']=float(np.min(np.abs((centered**3).mean(0)/(np.mean(centered**2,axis=0)**1.5))))
   for sigma in (.01,.05):
    for trial in range(3):
     noise=rng.normal(size=ca.shape);noise*=sigma/np.sqrt((noise**2).sum(1).mean())
     changed,_,_=module.canonicalize_coords((ca+noise).astype(np.float32))
     rmsd=float(np.sqrt(((changed-base)**2).sum(1).mean()))
     row['perturbations'].append(dict(input_displacement_rms=sigma,trial=trial,canonical_frame_rmsd=rmsd))
   rows.append(row)
 result=dict(status='complete',source=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),records=rows)
 a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# Canonical-frame stability on verified training structures','',f'{len(rows)} training proteins; exact inherited PCA/skewness implementation. No head training or GPU use.','',f"Largest frame difference after a proper rigid rotation and translation: {max(r['rigid_frame_rmsd'] for r in rows):.6f} Å.",'','| Input RMS perturbation | Proteins with any frame jump >1 Å | Fraction |','|---:|---:|---:|']
 for sigma in (.01,.05):
  count=sum(any(x['input_displacement_rms']==sigma and x['canonical_frame_rmsd']>1 for x in r['perturbations']) for r in rows)
  lines.append(f'| {sigma} Å | {count} | {count/len(rows):.4f} |')
 lines+=['','This tests coordinate-frame discontinuities. It does not measure their effect on encoded latents or establish that they limit prediction accuracy.']
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
