"""Necessary reachability bound under the already-fixed local geometry tolerances.

This is a diagnostic, not an alternative gate or sample-selection procedure.
Triangle bounds on disjoint one/two-bond groups ignore torsions and collisions,
so passing cannot prove feasibility. Exceeding the bound proves infeasibility.
"""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def angle(a,b):
    return np.arctan2(np.linalg.norm(np.cross(a,b)),np.dot(a,b))


def chain_bound(lengths,angles):
    """Tightest triangle bound from disjoint groups of one or two bonds."""
    dp=[0.]
    for n in range(1,len(lengths)+1):
        best=dp[-1]+lengths[n-1]+.05
        if n>=2:
            theta=min(np.pi,angles[n-2]+np.radians(10))
            # Convex in either length: maximum over the permitted rectangle is
            # attained at a corner. This also covers unusually acute parents.
            pair=max(np.sqrt(a*a+b*b-2*a*b*np.cos(theta))
                     for a in (max(0,lengths[n-2]-.05),lengths[n-2]+.05)
                     for b in (max(0,lengths[n-1]-.05),lengths[n-1]+.05))
            best=min(best,dp[-2]+pair)
        dp.append(best)
    return float(dp[-1])


def cone_projection(length,theta,axis,known_direction):
    alpha=angle(axis,known_direction)
    separation=max(0,abs(alpha-theta)-np.radians(10))
    cosine=np.cos(separation)
    return float((length+.05 if cosine>=0 else max(0,length-.05))*cosine)


def bounds(source,parent,start,motif_length,width=4):
    source=np.asarray(source,dtype=np.float64);parent=np.asarray(parent,dtype=np.float64)
    if source.shape!=parent.shape or source.ndim!=3 or source.shape[1:]!=(4,3) or not np.isfinite(source).all() or not np.isfinite(parent).all():
        raise ValueError('Finite matching backbone arrays required')
    n=len(source);regions=[]
    # Bound only bridges with fixed residues at BOTH ends; a terminal flank is
    # free-ended and has no two-anchor distance obstruction.
    if start-width-1>=0:regions.append(('left',start-width-1,start))
    if start+motif_length+width<n:regions.append(('right',start+motif_length-1,start+motif_length+width))
    results=[]
    for side,left,right in regions:
        path=[(left,2)]+[(r,a) for r in range(left+1,right) for a in (0,1,2)]+[(right,0)]
        p=np.array([parent[r,a] for r,a in path]);edges=np.diff(p,axis=0);lengths=np.linalg.norm(edges,axis=-1)
        if (lengths<1e-8).any():raise ValueError('Degenerate reference bond')
        angles=np.array([angle(-edges[i],edges[i+1]) for i in range(len(edges)-1)])
        delta=source[right,0]-source[left,2];required=np.linalg.norm(delta)
        loose=chain_bound(lengths,angles);oriented=loose
        if required>1e-8:
            axis=delta/required
            first_theta=angle(parent[left,1]-parent[left,2],edges[0])
            last_theta=np.pi-angle(-edges[-1],parent[right,1]-parent[right,0])
            first=cone_projection(lengths[0],first_theta,axis,source[left,1]-source[left,2])
            last=cone_projection(lengths[-1],last_theta,axis,source[right,1]-source[right,0])
            oriented=first+last+chain_bound(lengths[1:-1],angles[1:-1])
        upper=min(loose,oriented)
        results.append(dict(side=side,left_fixed_residue=left,right_fixed_residue=right,bonds=len(lengths),
            required_distance=float(required),triangle_upper_bound=loose,oriented_upper_bound=float(oriented),
            upper_bound=float(upper),excess=float(required-upper),impossible=bool(required>upper+1e-7)))
    return results


def analyze(run,report):
    m=json.loads((run/'manifest.json').read_text());d=json.loads(report.read_text());c=m['config']
    if d['status']!='complete' or d['manifest_sha256']!=sha(run/'manifest.json') or d['predictions_sha256']!=sha(run/'predictions.h5'):
        raise ValueError('Complete independently audited closure required')
    ids=[r['id'] for r in c['selected']];items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');rows=[]
    with h5py.File(c['source_predictions']) as f:
        for row in d['records']:
            arm,ident,slot=row['arm'],row['target_id'],row['generation_slot'];item=items[ident]
            parent=f[('native_direct' if arm=='native_cond' else 'parent')+'/'+ident+'/backbone'][slot]
            source=f[arm+'/'+ident+'/backbone'][slot]
            result=bounds(source,parent,item['start'],20)
            impossible=any(r['impossible'] for r in result)
            if impossible and row['local_geometry']['valid']:raise ValueError('Bound contradicts independently measured geometry')
            rows.append(dict(arm=arm,target_id=ident,slot=slot,bucket=row['bucket'],bounds=result,
                impossible=impossible,qualified_raw=row['qualified_raw'],local_geometry=row['local_geometry']['valid']))
    summaries=[]
    for arm in c['spec']['execution']['arms']:
        for bucket in (None,128,256,384,512):
            rr=[r for r in rows if r['arm']==arm and (bucket is None or r['bucket']==bucket)]
            summaries.append(dict(arm=arm,bucket=bucket,samples=len(rr),proven_impossible=sum(r['impossible'] for r in rr),
                qualified_raw=sum(r['qualified_raw'] for r in rr),not_excluded_but_geometry_failed=sum(not r['impossible'] and not r['local_geometry'] for r in rr)))
    return dict(status='complete',source_report_sha256=sha(report),summary=summaries,records=rows,
        scope='Posthoc necessary geometric bound using the existing0.05A/10degree tolerances and fixed endpoints. No new gate or filtering. Torsions, sterics and coupled orientations are relaxed, so not-excluded does not mean feasible. Every successful measured geometry must obey the bound.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.run,a.report);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Local closure reachability\n\n'+d['scope']+'\n\n```json\n'+json.dumps(d['summary'],indent=2)+'\n```\n')
    print(json.dumps([r for r in d['summary'] if r['bucket'] is None]))


if __name__=='__main__':main()
