"""Fixed within-corpus augmentation contrasts on additional experimental families."""
import json
from pathlib import Path
import h5py,torch
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from prepare_overfit import sha


def audit_config(c):
    for row in c['sources']:
        if sha(row['path'])!=row['sha256']:raise ValueError('Changed additional-validation source')
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['model_manifest']).read_text());d=json.loads(Path(c['model_report']).read_text());dm=json.loads(Path(c['data_manifest']).read_text());dd=json.loads(Path(c['data_report']).read_text());pc=m['config'];arm=c['arm']
    if spec!=c['spec'] or arm not in spec['parents'] or Path(c['model_manifest']).parent.name!=spec['parents'][arm] or m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(c['model_manifest']) or d['total_training_updates']!=spec['total_updates'][arm]:raise ValueError('Changed completed model')
    if pc.get('training_protein_count')!=int(arm[-3:]) or pc['distance_precision']!='fp64' or c['historical_fragments']!=pc['fragments'] or c['decoder_checkpoint']!=pc['decoder_checkpoint'] or c['control_ids']!=pc['control_ids']:raise ValueError('Changed conditioning architecture or historical inputs')
    run=Path(c['model_manifest']).parent
    if c['checkpoint']!=str(run/'ema_2000.ckpt') or c['historical_predictions']!=str(run/'evaluation_2000.h5'):raise ValueError('Changed final checkpoint')
    if dm['status']!='complete' or dd['status']!='complete' or not dd['generation_gate_passed'] or dd['manifest_sha256']!=sha(c['data_manifest']) or dd['fragments_sha256']!=sha(c['fragments']) or Path(c['data_manifest']).parent.name!=spec['encoded_cohort'] or Path(dm['config']['selection']).parent.name!=spec['selection'] or dm['config']['decoder_checkpoint']!=c['decoder_checkpoint']:raise ValueError('Unqualified additional fragments')
    if (spec['samples'],spec['batch_size'],spec['steps'],spec['decoder_steps'],spec['guidance'])!=(4,4,50,3,1):raise ValueError('Changed fixed sampler')
    with h5py.File(c['fragments']) as f:
        if len(c['target_ids'])!=64 or c['target_ids']!=sorted(f['development']) or len(c['control_ids'])!=4 or set(c['target_ids'])&set(c['control_ids']):raise ValueError('Changed new/historical cohorts')
    return spec


def load_conditions(path,ids):
    result={}
    with h5py.File(path) as f:
        for ident in ids:
            g=f['development/'+ident];q=g['conditions/f30_center'];n=int(g.attrs['length']);start=int(q.attrs['start']);fragment=q['fragment'][:];features,keep=fragment_features(torch.from_numpy(q['latent'][:]),q.attrs['sequence'],length=n,start=start)
            result[ident]=dict(length=n,family=str(g.attrs['family']),start=start,fragment=fragment,features=features,keep=keep,coordinates=fragment_coordinates(torch.from_numpy(fragment),length=n,start=start))
    return result
