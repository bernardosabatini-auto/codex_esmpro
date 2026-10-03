"""Training-only source selection and strict lineage for preference calibration."""
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from prepare_overfit import sha


def native_inventory(c):
    rows = {}
    for source in c['native_sources']:
        m = json.loads(Path(source['manifest']).read_text())
        d = json.loads(Path(source['report']).read_text())
        if (m['status'] != 'complete' or d['status'] != 'complete'
                or d['manifest_sha256'] != sha(source['manifest'])
                or d['refolded_sha256'] != sha(source['refolded'])):
            raise ValueError('Unaudited native reference source')
        for r in d['records']:
            if r['arm'] != 'original512': continue
            ident = r['target_id']
            if ident in rows: raise ValueError('Duplicate reference source')
            rows[ident] = dict(id=ident, family=r['family'], length=r['length'],
                              bucket=(r['length'] + 127)//128*128,
                              native_report=source['report'], native_name=r['name'])
    if len(rows) != 64: raise ValueError('Expected unchanged64 original-source references')
    return rows


def select_sources(spec, inventory, excluded, *, per_bucket=8):
    selected = []
    for bucket in (128, 256, 384, 512):
        pool = [r for r in inventory.values() if r['bucket'] == bucket and r['id'] not in excluded]
        pool.sort(key=lambda r: hashlib.sha256(f"{spec['selection_seed']}:{r['id']}".encode()).hexdigest())
        if len(pool) < per_bucket: raise ValueError('Insufficient prespecified training stratum')
        selected.extend(dict(r, partition=k % 4) for k, r in enumerate(pool[:per_bucket]))
    return selected


def audit_generation(c):
    if c.get('spec',{}).get('native_anchor_model_validation'):
        from native_anchor_model_validation import audit_generation as audit_model
        return audit_model(c)
    for source in c['sources']:
        if sha(source['path']) != source['sha256']: raise ValueError('Changed calibration source')
    spec = json.loads(Path(c['protocol']).read_text())
    if (spec != c['spec'] or not spec.get('training_preference_calibration')
            or spec['cohort'] != 'train' or spec['historical_cohort'] != 'train'
            or c['arm'] != 'parent6000' or spec['condition'] != 'c20_center'
            or tuple(spec[k] for k in ('samples','steps','decoder_steps','batch_size','guidance')) != (4,50,3,4,1)):
        raise ValueError('Changed training-only generation recipe')
    m = json.loads(Path(c['model_manifest']).read_text())
    d = json.loads(Path(c['model_report']).read_text())
    parent = Path(c['model_manifest']).parent
    if (parent.name != spec['parent'] or m['status'] != 'complete' or d['status'] != 'complete'
            or d['manifest_sha256'] != sha(c['model_manifest']) or d['total_training_updates'] != 6000
            or c['checkpoint'] != str(parent/'ema_2000.ckpt')
            or c['historical_predictions'] != str(parent/'evaluation_2000.h5')
            or c['decoder_checkpoint'] != m['config']['decoder_checkpoint']
            or c['historical_fragments'] != m['config']['fragments']):
        raise ValueError('Wrong frozen conditioning parent')
    dm = json.loads(Path(c['data_manifest']).read_text())
    dd = json.loads(Path(c['data_report']).read_text())
    if (dm['status'] != 'complete' or dd['status'] != 'complete' or not dd['training_gate_passed']
            or dd['manifest_sha256'] != sha(c['data_manifest'])
            or dd['fragments_sha256'] != sha(c['fragments']) or dm['training_protein_count'] != 512
            or dm['config']['base_fragments_sha256'] != m['config']['fragments_sha256']):
        raise ValueError('Wrong preserved512 corpus')
    inventory = native_inventory(c)
    excluded = json.loads(Path(c['excluded_feedback_manifest']).read_text())['config']['selected_training_ids']
    if spec.get('native_anchor_calibration'):
        previous=json.loads(Path(c['previous_generation_manifest']).read_text())
        previous_report=json.loads(Path(c['previous_generation_report']).read_text())
        if (Path(c['previous_generation_manifest']).parent.name!=spec['previous_generation']
                or previous['status']!='complete' or previous_report['status']!='complete'
                or previous_report['manifest_sha256']!=sha(c['previous_generation_manifest'])
                or len(previous['config']['target_ids'])!=32 or spec['native_samples']!=2):
            raise ValueError('Wrong excluded prior collection or native decoder budget')
        excluded=set(excluded)|set(previous['config']['target_ids'])
    selected = select_sources(spec, inventory, excluded, per_bucket=4 if spec.get('native_anchor_calibration') else 8)
    if selected != c['selected'] or c['target_ids'] != sorted(r['id'] for r in selected):
        raise ValueError('Changed prospective selection')
    with h5py.File(c['fragments']) as f:
        if not set(c['target_ids']) <= set(f['train']) or set(c['target_ids']) & set(f['development']):
            raise ValueError('Nontraining calibration target')
        controls = [min(i for i in m['config']['evaluation_train_ids']
                        if (int(f['train/'+i].attrs['length'])+127)//128*128 == b)
                    for b in (128,256,384,512)]
        if c['control_ids'] != controls: raise ValueError('Changed historical training controls')
        for r in selected:
            g = f['train/'+r['id']]; q = g['conditions/c20_center']
            if int(g.attrs['length']) != r['length'] or len(q.attrs['sequence']) != 20:
                raise ValueError('Changed supplied training fragment')
            report = json.loads(Path(r['native_report']).read_text())
            native = next(x for x in report['records'] if x['name'] == r['native_name'])
            if native['fixed_sequence'] != q.attrs['sequence'] or native['fixed_start'] != int(q.attrs['start']):
                raise ValueError('Reference constraint differs')
            source = next(x for x in c['native_sources'] if x['report'] == r['native_report'])
            with h5py.File(source['predictions']) as raw:
                if not np.array_equal(raw[native['dataset']][0],g['reference_backbone'][:]) or not np.array_equal(raw['motifs/'+r['id']][:],q['fragment'][:]):
                    raise ValueError('Reference coordinates differ')
    profile = json.loads(Path(c['generation_profile_report']).read_text())
    pm = json.loads(Path(c['generation_profile_manifest']).read_text())
    if (profile['status'] != 'complete' or profile['controls'] != 132
            or profile['manifest_sha256'] != sha(c['generation_profile_manifest'])
            or pm['config']['checkpoint'] != c['checkpoint']
            or any(r['peak_reserved_GiB'] > 75 for r in pm['batches'])):
        raise ValueError('Unqualified inherited generation profile')
    return spec
