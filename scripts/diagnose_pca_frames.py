"""Measure independent PCA-frame changes on already reference-aligned conformers."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from scipy.stats import skew


def frame(ca):
    # Match the read-only original canonicalize.py's CA PCA/skewness convention.
    x=ca-ca.mean(0);values,vectors=np.linalg.eigh(x.T@x/len(x));order=np.argsort(values)[::-1]
    values=values[order];vectors=vectors[:,order];projected=x@vectors
    for i in range(3):
        if skew(projected[:,i])<0:vectors[:,i]*=-1
    if np.linalg.det(vectors)<0:vectors[:,2]*=-1
    ratios=values[1:]/values[:-1]
    return vectors,bool((ratios>.9).any())


def main():
    p=argparse.ArgumentParser();p.add_argument('--shards',nargs=4,type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[];sources={};seen=set()
    for run in a.shards:
        metadata=json.loads((run/'manifest.json').read_text())
        if metadata['status']!='complete' or metadata['config']['latent_frame']!='teacher_CA_aligned_to_cached_reference':raise ValueError('fixed-frame inputs required')
        path=run/'labels.h5'
        with path.open('rb') as handle:sources[str(path)]=hashlib.file_digest(handle,'sha256').hexdigest()
        with h5py.File(path) as f:
            for ident in f:
                if ident in seen:raise ValueError('duplicate target')
                seen.add(ident);g=f[ident];reference,ref_degenerate=frame(g['reference_backbone'][:,1,:]);angles=[];flags=[]
                for ca in g['teacher_backbone'][:,:,1,:]:
                    rotation,degenerate=frame(ca)
                    angle=np.degrees(np.arccos(np.clip((np.trace(rotation@reference.T)-1)/2,-1,1)))
                    angles.append(float(angle));flags.append(degenerate)
                rows.append(dict(id=ident,angles_degrees=angles,reference_near_degenerate=ref_degenerate,teacher_near_degenerate=flags))
    if len(rows)!=512:raise ValueError('expected 512 training families')
    angles=np.asarray([r['angles_degrees'] for r in rows]);flags=np.asarray([r['teacher_near_degenerate'] for r in rows])
    d=dict(status='complete',sources=sources,rows=rows,summary=dict(teacher_samples=angles.size,median_frame_angle_degrees=float(np.median(angles)),fraction_over_90_degrees=float((angles>90).mean()),families_with_any_over_90=int((angles>90).any(1).sum()),teacher_near_degenerate_fraction=float(flags.mean()),reference_near_degenerate_count=sum(r['reference_near_degenerate'] for r in rows)))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Independent PCA frames on aligned teacher conformers','','All teacher inputs were first globally fitted into their cached reference frame. This diagnostic measures the additional orientation introduced by independently applying the inherited PCA/skewness rule to each conformation. Angles combine continuous axis shifts and discrete sign/axis changes; they do not isolate eigenvalue degeneracy and are not an accuracy result.','']
    lines += [f'- {k}: {v}' for k,v in d['summary'].items()]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
