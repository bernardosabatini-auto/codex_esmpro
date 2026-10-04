"""Bound three-pass whole-scaffold refresh using only generated complete inputs."""
import json
from pathlib import Path
import torch
from context_refresh_frame_core import audit as audit_frame
from prepare_overfit import sha


def sources(c):
    return c['sources']+c['frame_config']['sources']+c['frame_config']['base']['sources']


def file_stats(c):
    rows=[]
    for p in sorted({r['path'] for r in sources(c)}):
        s=Path(p).stat();rows.append(dict(path=p,size=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino))
    return rows


def audit(c,*,full=True):
    if full:
        audit_frame(c['frame_config'])
        for r in c['sources']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed refresh source: '+r['path'])
    elif file_stats(c)!=c['cpu_verified_file_stats']:raise ValueError('Refresh source metadata changed')
    fc=c['frame_config'];base=fc['base'];parent=json.loads(Path(base['source_manifest']).read_text());gc=parent['config']
    f=json.loads(Path(c['frame_report']).read_text());fm=json.loads(Path(c['frame_manifest']).read_text())
    closure=json.loads(Path(base['closure_report']).read_text());spec=fc['spec']
    expected=[r for r in gc['selected'] if not c['profile_only'] or r in fc['selected']]
    if (c['selected']!=expected or fm['config']!=fc or not f['qualified'] or not f['numerically_qualified']
            or f['manifest_sha256']!=sha(c['frame_manifest']) or f['protocol_sha256']!=sha(fc['protocol'])
            or closure['predictions_sha256']!=next(r['sha256'] for r in c['sources'] if r['path']==c['starting_backbones'])
            or Path(c['starting_backbones']).parent.name!=spec['source_closure']):raise ValueError('Unqualified refresh prerequisite')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text());pm=json.loads(Path(c['profile_manifest']).read_text())
        if (not p['profile_only'] or not p['qualified'] or not p['numerically_qualified'] or pm['config']['frame_config']!=fc
                or p['manifest_sha256']!=sha(c['profile_manifest']) or p['predictions_sha256']!=sha(c['profile_predictions'])):
            raise ValueError('Unqualified iterative profile')
    return spec,gc,parent


def starting_state(backbones,keep):
    if backbones.shape!=(*keep.shape,4,3) or keep.dtype!=torch.bool or not torch.isfinite(backbones).all():
        raise ValueError('Finite complete generated backbones and exact motif mask required')
    centered=backbones-backbones.mean((1,2),keepdim=True)
    anchors=torch.where(keep[...,None,None],centered,torch.zeros_like(centered))
    return centered,anchors


def refresh_rounds(current,encode,decode,*,rounds=3):
    if rounds!=3:raise ValueError('Exactly three prospective context refreshes required')
    for index in range(1,4):
        latent=encode(current);result=decode(latent)
        if result.shape!=current.shape or not torch.isfinite(result).all():raise ValueError('Invalid refreshed backbone')
        yield index,current,latent,result
        current=result
