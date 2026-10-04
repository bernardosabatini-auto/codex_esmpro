"""Slot-specific isolated inputs for a frozen compatibility diagnostic."""
import json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from generate_isolated_motif import canonical_fragment
from latentfold.backbone import encode_backbone
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from latentfold.fragment_inpainting import place_fragment
from prepare_overfit import sha


def assemble_inputs(reference,sequence,start,encode,*,posed=False):
    """Encoder sees one cropped fragment at a time, never the full backbone."""
    if reference.ndim!=4 or reference.shape[2:]!=(4,3) or start<0 or start+len(sequence)>reference.shape[1]:
        raise ValueError('Matching parent batch and contained fragment required')
    fragments=[];codes=[];features=[];keeps=[];coords=[];anchors=[]
    rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64)
    for slot in range(len(reference)):
        raw=reference[slot,start:start+len(sequence)].detach().cpu().numpy().astype(np.float64)
        if posed:raw=raw@rotation+np.array([11,7,-3],dtype=np.float64)
        isolated,_=canonical_fragment(raw)
        fragment=torch.from_numpy(isolated).to(reference)
        latent=encode(fragment[None])[0]
        feat,keep=fragment_features(latent,sequence,length=reference.shape[1],start=start)
        coord=fragment_coordinates(fragment,length=reference.shape[1],start=start)
        anchor=place_fragment(fragment,reference[slot:slot+1],start)[0]
        fragments.append(fragment);codes.append(latent);features.append(feat);keeps.append(keep);coords.append(coord);anchors.append(anchor)
    return dict(fragment=torch.stack(fragments),isolated_latent=torch.stack(codes),features=torch.stack(features),
                keep=torch.stack(keeps),coordinates=torch.stack(coords),anchors=torch.stack(anchors))


def encoder(codec,fragment):
    mask=torch.ones(fragment.shape[:2],dtype=torch.bool,device=fragment.device)
    return F.layer_norm(encode_backbone(codec,fragment,mask),(8,))


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed compatibility source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['source_manifest']).read_text());gc=m['config']
    d=json.loads(Path(c['source_report']).read_text());closure=json.loads(Path(c['closure_report']).read_text())
    for key in ('reachability_report','closure_effects_report'):
        report=json.loads(Path(c[key]).read_text())
        if report['status']!='complete' or report['source_report_sha256']!=sha(c['closure_report']):
            raise ValueError('Unbound closure diagnosis')
    if (spec!=c['spec'] or m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified']
            or not d['junction_weighted'] or d['qualified'] or d['profile_only']
            or Path(c['source_manifest']).parent.name!=spec['parent_run']
            or d['manifest_sha256']!=sha(c['source_manifest']) or d['predictions_sha256']!=sha(c['source_predictions'])
            or m['checkpoint_sha256']!=sha(c['checkpoint']) or c['selected']!=gc['selected'] or len(c['selected'])!=32
            or any(c[k]!=gc[k] for k in ('fragments','decoder_checkpoint'))
            or closure['status']!='complete' or closure['profile_only'] or closure['qualified']
            or closure['summary'][0]['qualified_raw']!=30 or closure['protocol_sha256']!=sha(c['closure_protocol'])):
        raise ValueError('Unbound failed original-condition prerequisites')
    return spec,gc,m
