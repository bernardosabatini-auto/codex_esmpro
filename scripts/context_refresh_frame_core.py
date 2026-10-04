"""Mandatory encoder/frame prerequisite for frozen whole-scaffold refresh."""
import json
from pathlib import Path
import numpy as np
from compatible_fragment_core import audit as audit_compatible
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def file_stats(c):
    paths=sorted({r['path'] for r in c['sources']+c['base']['sources']})
    result=[]
    for p in paths:
        s=Path(p).stat();result.append(dict(path=p,size=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino))
    return result


def audit(c,*,full=True):
    if full:
        audit_compatible(c['base'])
        for r in c['sources']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed frame prerequisite source: '+r['path'])
    elif c['cpu_verified_file_stats']!=file_stats(c):raise ValueError('Source metadata changed after CPU preflight')
    spec=json.loads(Path(c['protocol']).read_text());d=json.loads(Path(c['compatible_report']).read_text())
    m=json.loads(Path(c['base']['source_manifest']).read_text());gc=m['config']
    profile=[next(r for r in gc['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    if (c['spec']!=spec or c['selected']!=profile or d['status']!='complete' or not d['numerically_qualified']
            or d['next_route']!='global_scaffold_remodeling' or d['summary'][0]['closed_complete']!=127
            or Path(c['base']['source_manifest']).parent.name!=spec['source_training']
            or spec['rounds']!=3 or spec['resources']['precision']!='fp32'):
        raise ValueError('Unbound whole-context refresh prerequisite')
    return gc,m


def frame_metrics(backbones,reference):
    if backbones.shape!=reference.shape or backbones.shape[0]!=4:raise ValueError('Four matching complete backbones required')
    valid=backbone_geometry(backbones)['coarse_valid'];rows=[]
    for slot,(bb,ref) in enumerate(zip(backbones,reference)):
        p,q=bb[:,1].astype(float),ref[:,1].astype(float)
        proper=ca_metrics(p,q)['ca_rmsd'];centered=float(np.sqrt(np.mean(np.sum(((p-p.mean(0))-(q-q.mean(0)))**2,axis=1))))
        rows.append(dict(slot=slot,coarse_valid=bool(valid[slot]),proper_ca_rmsd=proper,centered_ca_rmsd=centered,
                         reconstruction_pass=bool(valid[slot] and proper<=1),frame_pass=centered<=proper+.1))
    return rows


def frame_gate(rows):
    wanted={(a,i,k) for a in ('parent','native_direct') for i in {r['target_id'] for r in rows} for k in range(4)}
    if len(wanted)!=32 or len(rows)!=32 or {(r['arm'],r['target_id'],r['slot']) for r in rows}!=wanted:
        raise ValueError('Incomplete encoder-frame denominator')
    return all(sum(r['reconstruction_pass'] for r in rows if r['arm']==a)>=15 for a in ('parent','native_direct')) and all(r['frame_pass'] for r in rows)
