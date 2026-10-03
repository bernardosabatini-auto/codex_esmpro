"""Immutable recipe and source inventory for learned masked latent repair."""
import json
from pathlib import Path
import h5py
import torch
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from prepare_overfit import sha


def audit(c):
    from decoder_fragment_variance_core import audit as previous_audit
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed masked-repair source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());previous=json.loads(Path(c['diagnostic_manifest']).read_text());report=json.loads(Path(c['diagnostic_report']).read_text());pc=previous['config'];previous_audit(pc)
    if (spec!=c['spec'] or previous['status']!='complete' or report['status']!='complete'
        or Path(c['diagnostic_manifest']).parent.name!=spec['diagnostic'] or report['manifest_sha256']!=sha(c['diagnostic_manifest'])
        or previous['predictions_sha256']!=sha(c['diagnostic_predictions']) or report['predictions_sha256']!=previous['predictions_sha256']
        or report['historical_predictions_audited']!=128 or report['native_batch_controls']!=32
        or c['selected']!=pc['selected'] or c['fragments']!=pc['fragments'] or c['decoder_checkpoint']!=pc['decoder_checkpoint']
        or c['baseline_predictions']!=pc['baseline_predictions'] or Path(pc['baseline_manifest']).parent.name!=spec['baseline_generation']
        or c['updates']!=(spec['profile_updates'] if c['profile_only'] else spec['updates'])):raise ValueError('Changed repair protocol/lineage')
    with h5py.File(c['fragments']) as f:
        if sorted(f['train'])!=c['training_ids'] or len(c['training_ids'])!=512:raise ValueError('Changed repair training inventory')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if p['status']!='complete' or not p['profile_only'] or not p['qualified'] or p['protocol_sha256']!=sha(c['protocol']) or p['fragments_sha256']!=sha(c['fragments']) or c['allocation_minutes']!=p['recommended_full_minutes']:raise ValueError('Unqualified masked-repair profile')
    return spec


def load_training(c):
    data={}
    with h5py.File(c['fragments']) as f:
        for ident in c['training_ids']:
            g=f['train/'+ident];z=torch.from_numpy(g['reference_z'][:]);n=len(z);conditions={}
            if z.shape!=(n,8) or not torch.isfinite(z).all() or not 20<=n<=512:raise ValueError('Invalid native endpoint')
            for name in c['spec']['conditions']:
                q=g['conditions/'+name];start=int(q.attrs['start']);fragment=torch.from_numpy(q['fragment'][:]);features,keep=fragment_features(torch.from_numpy(q['latent'][:]),str(q.attrs['sequence']),length=n,start=start)
                if len(fragment)!=20:raise ValueError('Changed supplied motif length')
                conditions[name]=dict(features=features,keep=keep,coordinates=fragment_coordinates(fragment,length=n,start=start))
            data[ident]=dict(length=n,bucket=((n+127)//128)*128,target=z,conditions=conditions)
    return data


def training_batch(data,ids,names,length):
    b=len(ids);z=torch.zeros(b,length,8);features=torch.zeros(b,length,29);keep=torch.zeros(b,length,dtype=torch.bool);mask=torch.zeros_like(keep);coords=torch.zeros(b,length,3)
    for k,(ident,name) in enumerate(zip(ids,names)):
        p=data[ident];q=p['conditions'][name];n=p['length'];z[k,:n]=p['target'];features[k,:n]=q['features'];keep[k,:n]=q['keep'];coords[k,:n]=q['coordinates'];mask[k,:n]=True
    return z,features,keep,mask,coords


def panel(c):
    if not c['profile_only']:return c['selected']
    return [next(r for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)]
