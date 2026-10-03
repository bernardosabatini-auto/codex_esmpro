"""Immutable inputs and CPU scoring for bounded decoder-only corrections."""
import json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry


def audit_config(c,decoder=False):
    for key in ('protocol','parent_manifest','parent_report','parent_predictions','fragments')+ (('decoder_checkpoint',) if decoder else ()):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed endpoint guidance source: '+key)
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['parent_manifest']).read_text());d=json.loads(Path(c['parent_report']).read_text())
    if c['spec']!=spec or Path(c['parent_manifest']).parent.name!=spec['parent'] or m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=c['parent_manifest_sha256'] or d['total_training_updates']!=6000:raise ValueError('Wrong completed conditioner')
    pc=m['config']
    if c['target_ids']!=pc['control_ids'] or len(c['target_ids'])!=4 or c['fragments_sha256']!=pc['fragments_sha256'] or c['decoder_checkpoint_sha256']!=pc['decoder_checkpoint_sha256']:raise ValueError('Changed panel or decoder')
    if spec.get('validity_guarded'):
        from fragment_validation_core import audit_config as audit_validation
        for key in ('fresh_validation_manifest','fresh_validation_report'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed fresh endpoint input')
        vm=json.loads(Path(c['fresh_validation_manifest']).read_text());vd=json.loads(Path(c['fresh_validation_report']).read_text());vc=vm['config'];audit_validation(vc)
        model=vc['models'][spec['prediction_prefix']]
        if vm['status']!='complete' or vd['status']!='complete' or vd['manifest_sha256']!=c['fresh_validation_manifest_sha256'] or vm['predictions_sha256']!=c['parent_predictions_sha256'] or Path(c['fresh_validation_manifest']).parent.name!=spec['fresh_validation'] or Path(c['parent_predictions'])!=Path(c['fresh_validation_manifest']).parent/'predictions.h5' or model['manifest']!=c['parent_manifest'] or vc['spec']['seed']!=spec['generation_seed']:raise ValueError('Changed fresh endpoint cohort')
    elif Path(c['parent_predictions']).name!='evaluation_2000.h5':raise ValueError('Changed historical endpoint input')
    if (spec['samples'],spec['max_updates'],spec['relative_radius'],spec['desired_rmsd'])!=(4,12,.05,.5) or spec['line_search_steps']!=[.01,.005,.0025,.00125]:raise ValueError('Undeclared correction recipe')
    return spec


def score(backbones,fragment,start):
    valid=backbone_geometry(backbones)['coarse_valid'];rows=[]
    for k,x in enumerate(backbones):
        fit=motif_fit(x,fragment,start);rows.append(dict(slot=k,coarse_valid=bool(valid[k]),raw_gate_passed=bool(valid[k] and fit['motif_drms']<=1 and fit['motif_ca_rmsd']<=1),**fit))
    return rows


def retract_numpy(proposal,reference):
    mu=reference.mean(-1,keepdims=True);radius=np.linalg.norm(reference-mu,axis=-1,keepdims=True);center=proposal-proposal.mean(-1,keepdims=True)
    return np.where(radius>1e-12,mu+center*radius/np.maximum(np.linalg.norm(center,axis=-1,keepdims=True),1e-12),reference)
