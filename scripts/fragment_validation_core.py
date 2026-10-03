"""Audits and cohort definitions for fresh-noise conditional validation."""
import json
from pathlib import Path
import h5py,numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from prepare_overfit import sha


def view_rows(rows,arm,view,focus):
    if view not in ('whole_panel','focus'):raise ValueError('Unknown validation view')
    return [r for r in rows if r['arm']==arm and (r['generation_slot']<4 if view=='whole_panel' else r['target_id']==focus)]


def raw_rows(bb,fragment,start,arm,ident,family):
    valid=backbone_geometry(bb)['coarse_valid'];rows=[]
    for slot,(x,v) in enumerate(zip(bb,valid)):
        fit=motif_fit(x,fragment,start)
        rows.append(dict(arm=arm,target_id=ident,family=family,generation_slot=slot,length=len(x),coarse_valid=bool(v),raw_gate_passed=bool(v and fit['motif_drms']<=1 and fit['motif_ca_rmsd']<=1),**fit))
    return rows


def audit_config(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed fresh-noise source')
    if json.loads(Path(c['protocol']).read_text())!=c['spec']:raise ValueError('Changed prospective recipe')
    spec=c['spec']
    if tuple(spec[k] for k in ('panel_samples','focus_samples','batch_size','steps','decoder_steps','guidance'))!=(4,16,4,50,3,1) or spec['condition']!='f30_center':raise ValueError('Changed fixed sampling recipe')
    if set(c['models'])!=set(spec['parents']) or len(c['target_ids'])!=16 or spec['focus_id'] not in c['target_ids']:raise ValueError('Changed validation inventory')
    for arm,r in c['models'].items():
        m=json.loads(Path(r['manifest']).read_text());d=json.loads(Path(r['report']).read_text())
        if Path(r['manifest']).parent.name!=spec['parents'][arm] or m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(r['manifest']) or d['total_training_updates']!=spec.get('total_updates',{}).get(arm,6000):raise ValueError('Unaudited validation model')
        for key in ('fragments','decoder_checkpoint','native_predictions'):
            source='initial_predictions' if key=='native_predictions' else key
            if c[key]!=m['config'][source]:raise ValueError('Different validation input')
        if r['checkpoint']!=str(Path(r['manifest']).parent/'ema_2000.ckpt') or r['historical_predictions']!=str(Path(r['manifest']).parent/'evaluation_2000.h5'):raise ValueError('Changed model checkpoint')
    with h5py.File(c['fragments']) as f:
        if sorted(f['development'])!=c['target_ids']:raise ValueError('Changed entire development panel')
    d=json.loads(Path(c['discovery_report']).read_text())
    if d['status']!='complete' or not d['native_strict_controls'][spec['focus_id']] or not any(r['target_id']==spec['focus_id'] and r['arm']==spec.get('discovery_arm','weighted_extended') and r['strict_joint_success'] for r in d['records']):raise ValueError('Unqualified discovery')

    if spec.get('discovery_scaffold_report'):
        scaffold=json.loads(Path(c['discovery_scaffold_report']).read_text())
        if scaffold['status']!='complete' or scaffold['source_report_sha256']!=sha(c['discovery_report']):raise ValueError('Changed discovery scaffold evidence')
        require_scaffold_discovery(spec,scaffold['rows'])


def require_scaffold_discovery(spec,rows):
    if not any(r['target_id']==spec['focus_id'] and r['arm']==spec['discovery_arm'] and r['primary_joint_success'] and r['scaffold_joint_success'] for r in rows):raise ValueError('Discovery lacks same-refold scaffold agreement')
