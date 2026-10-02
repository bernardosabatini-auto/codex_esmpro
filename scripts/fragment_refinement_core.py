"""Reference-free feedback selection and audited same-refold scoring."""
import json
from pathlib import Path
import h5py
import numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit, same_refold_success
from latentfold.metrics import usalign_coordinates
from fixed_motif_design import verify_fixed_sequences
from prepare_overfit import sha


def choose_refold(rows):
    valid = [r for r in rows if r['coarse_valid']]
    return min(valid, key=lambda r: (r['motif_ca_rmsd'], r['motif_drms'],
                                    -r['sc_tm'], r['sequence_index']))['sequence_index'] if valid else None


def audit_config(c):
    for dep in c['sources']:
        if sha(dep['path']) != dep['sha256']:
            raise ValueError('Changed refinement source: ' + dep['path'])
    spec = json.loads(Path(c['protocol']).read_text())
    if spec != c['spec'] or [r['target_id'] for r in c['cases']] != spec['cases']:
        raise ValueError('Changed prospective refinement recipe')


def score_assay(run):
    run = Path(run)
    m = json.loads((run/'manifest.json').read_text())
    if m['status'] != 'complete':
        raise ValueError('Incomplete refinement assay')
    c = m['config']
    for key in ('predictions','generation_manifest','protocol','usalign'):
        if sha(c[key]) != c[key+'_sha256']:
            raise ValueError('Changed assay ' + key)
    verify_fixed_sequences(m['sequences'], c['entries'])
    expected = {(r['name'],k) for r in c['entries'] for k in range(8)}
    indexed = {(r['name'],r['sequence_index']):r for r in m['records']}
    if len(indexed) != len(m['records']) or set(indexed) != expected or m['training_updates_executed']:
        raise ValueError('Changed refold inventory')
    controls = {r['name']:r for r in m['controls']}
    if len(controls) != len(m['controls']) or set(controls) != {r['name'] for r in c['entries'] if r['repeatability_control']} or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in controls.values()):
        raise ValueError('Teacher repeatability failed')
    result = []
    with h5py.File(c['predictions']) as raw, h5py.File(run/'refolded.h5') as folds:
        if set(folds) != {r['name'] for r in c['entries']}:
            raise ValueError('Extra refold groups')
        for r in c['entries']:
            bb = raw[r['dataset']][0]
            fragment = raw['motifs/'+r['target_id']][:]
            first = dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),
                         **motif_fit(bb,fragment,r['motif_start']))
            rows = []
            if set(folds[r['name']]) != set(map(str,range(8))):
                raise ValueError('Missing sequences')
            for k in range(8):
                x = folds[r['name']+'/'+str(k)][:]
                if x.shape != bb.shape or not np.isfinite(x).all():
                    raise ValueError('Invalid refold')
                tm = usalign_coordinates(c['usalign'],x[:,1],bb[:,1])
                if abs(tm-indexed[r['name'],k]['sc_tm'])>1e-7:
                    raise ValueError('Global score mismatch')
                rows.append(dict(sequence_index=k,sc_tm=tm,
                    coarse_valid=bool(backbone_geometry(x[None])['coarse_valid'][0]),
                    **motif_fit(x,fragment,r['motif_start'])))
            result.append(dict(**r,raw=first,refolds=rows,**same_refold_success(first,rows)))
    return result


def audit_assay(c):
    """Check generated inputs and isolate positive-control native coordinates."""
    if sha(c['pilot_config'])!=c['pilot_config_sha256']:raise ValueError('Changed pilot configuration')
    pilot=json.loads(Path(c['pilot_config']).read_text());gm=json.loads(Path(c['generation_manifest']).read_text())
    if gm['status']!='complete' or gm['config_sha256']!=c['pilot_config_sha256'] or gm['predictions_sha256']!=c['predictions_sha256'] or gm['entries']!=c['entries']:raise ValueError('Changed generation lineage')
    wanted={(arm,r['target_id']) for arm in ('feedback','random','native') for r in pilot['cases']}
    if len(c['entries'])!=6 or {(r['arm'],r['target_id']) for r in c['entries']}!=wanted:raise ValueError('Changed matched panel')
    for key,value in pilot['teacher_recipe'].items():
        if c[key]!=value:raise ValueError('Changed teacher recipe')
    with h5py.File(c['predictions']) as f,h5py.File(pilot['fragments']) as fr,h5py.File(pilot['native_predictions']) as native:
        for r in c['entries']:
            case=next(x for x in pilot['cases'] if x['target_id']==r['target_id']);q=fr['development/'+r['target_id']+'/conditions/'+pilot['spec']['condition']]
            if r['slot']!=0 or r['length']!=case['length'] or r['fixed_start']!=case['motif_start'] or r['motif_start']!=case['motif_start'] or r['fixed_sequence']!=case['fixed_sequence'] or r['repeatability_control']!=(r['arm']=='native'):raise ValueError('Changed supplied fragment')
            if not np.array_equal(f['motifs/'+r['target_id']][:],q['fragment'][:]):raise ValueError('Changed isolated fragment')
            if r['arm']=='native' and not np.array_equal(f[r['dataset']][0],native['references/'+r['target_id']+'/backbone'][:]):raise ValueError('Changed positive control')
