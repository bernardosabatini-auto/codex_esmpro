"""Outcome-independent designability sampling and immutable native-control reuse."""
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
from prepare_overfit import sha


def audit_refold_plan(spec):
    if not spec.get('refold_protocol'):
        if spec.get('designability_panel') or spec.get('native_runs'):
            raise ValueError('Unbound refold plan')
        return
    if sha(spec['refold_protocol']) != spec['refold_protocol_sha256']:
        raise ValueError('Changed prospective refold plan')
    plan = json.loads(Path(spec['refold_protocol']).read_text())
    if spec['designability_panel'] != plan['designability_panel'] or spec['native_runs'] != plan['native_runs'][spec['condition']]:
        raise ValueError('Changed declared panel or native sources')


def designability_ids(spec, items):
    panel = spec.get('designability_panel')
    if panel is None:
        return set()
    if panel != dict(families_per_length=16, slot=0, seed=2026100377):
        raise ValueError('Changed prospective designability panel')
    result = set()
    for short in (True, False):
        ids = sorted(i for i, q in items.items() if (q['length'] <= 256) == short)
        if len(ids) != 32:
            raise ValueError('Changed family length strata')
        for k in range(4):
            order = sorted(ids[k::4], key=lambda i: hashlib.sha256(f"{panel['seed']}:{i}".encode()).hexdigest())
            result.update(order[:4])
    if len(result) != 32:
        raise ValueError('Incomplete designability panel')
    return result


def audit_native_reuse(c, items, spec):
    if not spec.get('native_runs'):
        if c.get('native_reuse'):
            raise ValueError('Undeclared native-control reuse')
        return None
    source = c['native_reuse']
    for key in ('manifest', 'report', 'refolded', 'predictions'):
        if sha(source[key]) != source[key + '_sha256']:
            raise ValueError('Changed native-control evidence')
    m = json.loads(Path(source['manifest']).read_text())
    d = json.loads(Path(source['report']).read_text())
    old = m['config']
    if (Path(source['manifest']).parent.name != spec['native_runs'][c['partition']]
            or m['status'] != 'complete' or d['status'] != 'complete'
            or d['manifest_sha256'] != source['manifest_sha256']
            or d['refolded_sha256'] != source['refolded_sha256']
            or old['predictions_sha256'] != source['predictions_sha256']
            or old['fragments_sha256'] != c['fragments_sha256']
            or old['target_ids'] != c['target_ids'] or d['target_ids'] != c['target_ids']
            or set(d['native_controls']) != set(c['target_ids'])):
        raise ValueError('Mismatched native-control source')
    for key in ('num_sequences', 'temperature', 'mpnn_seed', 'seed', 'mpnn', 'dependencies',
                'teacher_artifacts', 'precision', 'usalign_sha256'):
        if old[key] != c[key]:
            raise ValueError('Changed native teacher recipe')
    entries = [r for r in old['entries'] if r['arm'] == 'native']
    if len(entries) != 16 or {r['target_id'] for r in entries} != set(c['target_ids']):
        raise ValueError('Incomplete native inventory')
    with h5py.File(source['predictions']) as raw, h5py.File(c['fragments']) as fragments:
        for r in entries:
            q = items[r['target_id']]
            if (r['fixed_sequence'] != q['sequence'] or r['fixed_start'] != q['start']
                    or not np.array_equal(raw['motifs/' + r['target_id']][:], q['fragment'])
                    or not np.array_equal(raw[r['dataset']][0], fragments['references/' + r['target_id'] + '/backbone'][:])):
                raise ValueError('Changed native constraint or coordinates')
    return d['native_controls']
