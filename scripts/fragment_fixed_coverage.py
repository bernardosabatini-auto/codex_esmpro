"""Reuse completed fixed-panel refolds without increasing the per-backbone budget."""
import json
from pathlib import Path

import h5py
import numpy as np

from fixed_motif_design import verify_fixed_sequences
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit, same_refold_success
from latentfold.metrics import usalign_coordinates
from prepare_overfit import sha


def bind_coverage(root, spec):
    return [dict(arm=arm, config=str(root/config), config_sha256=sha(root/config),
                 run=str(root/'runs'/run), native_run=str(root/'runs'/native))
            for arm, config, run, native in spec.get('covered_assays', [])]


def split_coverage(c, selected):
    spec = json.loads(Path(c['protocol']).read_text())
    root = Path(c['generation_manifest']).parents[2]
    covered = c.get('covered_assays', [])
    if covered != bind_coverage(root, spec):
        raise ValueError('Changed declared fixed-panel coverage')
    remaining, reused = dict(selected), []
    for source in covered:
        cfg = json.loads(Path(source['config']).read_text())
        if cfg['assay'] != 'trained_fragment' or cfg['num_sequences'] != 8 or sha(cfg['predictions']) != cfg['predictions_sha256']:
            raise ValueError('Changed fixed assay source')
        for key in ('num_sequences', 'temperature', 'mpnn_seed', 'seed', 'precision', 'dependencies', 'teacher_artifacts', 'usalign_sha256'):
            if cfg[key] != c[key]:
                raise ValueError('Covered design recipe differs')
        with h5py.File(cfg['predictions']) as f:
            for r in cfg['entries']:
                key = source['arm'], r['target_id'], r['slot']
                if r['mode'] != 'conditioned' or key not in remaining:
                    continue
                item = remaining[key]
                if r['fixed_sequence'] != item[2] or r['fixed_start'] != item[3] or r['motif_start'] != item[3] or not np.array_equal(f[r['dataset']][r['slot']], item[0]) or not np.array_equal(f['motifs/'+key[1]][:], item[1]):
                    raise ValueError('Covered backbone/motif differs')
                reused.append((source, r, remaining.pop(key)))
    return remaining, reused


def _completed_source(run, current):
    path = Path(run)
    mp = path/'manifest.json'
    rp = path.parents[1]/'reports'/(path.name+'.json')
    if not mp.exists() or not rp.exists():
        raise RuntimeError('Waiting for audited covered assay: '+path.name)
    m, report = json.loads(mp.read_text()), json.loads(rp.read_text())
    if m['status'] != 'complete' or report['status'] != 'complete' or report['manifest_sha256'] != sha(mp) or report['refolded_sha256'] != sha(path/'refolded.h5'):
        raise ValueError('Incomplete/changed covered assay')
    cfg = m['config']
    for key in ('num_sequences', 'temperature', 'mpnn_seed', 'seed', 'precision', 'dependencies', 'teacher_artifacts', 'usalign_sha256'):
        if cfg[key] != current[key]:
            raise ValueError('Covered teacher/design recipe differs')
    if sha(cfg['predictions']) != cfg['predictions_sha256']:
        raise ValueError('Changed covered raw inputs')
    verify_fixed_sequences(m['sequences'], cfg['entries'])
    if cfg['assay'] == 'trained_fragment' and not report['interpretation_qualified']:
        raise ValueError('Covered fixed assay controls failed')
    if any(r['ca_rmsd'] > .01 or r['ca_lddt'] < .999 for r in m['controls']):
        raise ValueError('Covered repeatability failed')
    return path, m, report


def _record(path, m, entry, item, arm, slot, usalign):
    name, ident = entry['name'], entry['target_id']
    with h5py.File(m['config']['predictions']) as rawfile, h5py.File(path/'refolded.h5') as refold:
        bb = rawfile[entry['dataset']][entry['slot']]
        fragment = rawfile['motifs/'+ident][:]
        if entry['fixed_sequence'] != item[2] or entry['fixed_start'] != item[3] or not np.array_equal(fragment, item[1]):
            raise ValueError('Covered fixed sequence/fragment changed')
        if arm != 'native' and not np.array_equal(bb, item[0]):
            raise ValueError('Covered generated backbone changed')
        raw = dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]), **motif_fit(bb, fragment, item[3]))
        rows = []
        original = [r for r in m['records'] if r['name'] == name]
        index = {r['sequence_index']: r for r in original}
        if len(original) != 8 or set(index) != set(range(8)) or set(refold[name]) != set(map(str, range(8))):
            raise ValueError('Covered refold budget/coverage changed')
        for k in range(8):
            x = refold[name+'/'+str(k)][:]
            if x.shape != bb.shape or not np.isfinite(x).all():
                raise ValueError('Invalid covered refold')
            tm = usalign_coordinates(usalign, x[:, 1], bb[:, 1])
            if abs(tm-index[k]['sc_tm']) > 1e-7:
                raise ValueError('Covered global metric differs')
            rows.append(dict(sequence_index=k, sc_tm=tm,
                coarse_valid=bool(backbone_geometry(x[None])['coarse_valid'][0]), **motif_fit(x, fragment, item[3])))
    return dict(name='covered_'+arm+'_'+ident+'_'+str(slot), arm=arm, target_id=ident,
        family=item[4], generation_slot=slot, motif_start=item[3], raw=raw, refolds=rows,
        reused_from=str(path), source_name=name, source_manifest_sha256=sha(path/'manifest.json'),
        **same_refold_success(raw, rows))


def collect_covered(c, selected):
    _, reused = split_coverage(c, selected)
    records, native_done = [], {r['target_id'] for r in c['entries'] if r['arm']=='native'}
    for source, entry, item in reused:
        path, m, _ = _completed_source(source['run'], c)
        if m['config'] != json.loads(Path(source['config']).read_text()):
            raise ValueError('Completed assay differs from its planned inputs')
        records.append(_record(path, m, entry, item, source['arm'], entry['slot'], c['usalign']))
        ident = entry['target_id']
        if ident not in native_done:
            path, m, _ = _completed_source(source['native_run'], c)
            native = [r for r in m['config']['entries'] if r['target_id'] == ident and r['fixed_sequence'] == item[2]]
            if len(native) != 1 or not native[0].get('repeatability_control') or {r['name'] for r in m['controls']} != {r['name'] for r in m['config']['entries']}:
                raise ValueError('Missing covered fixed-motif native control')
            with h5py.File(m['config']['predictions']) as old, h5py.File(c['native_predictions']) as reference:
                if not np.array_equal(old[native[0]['dataset']][native[0]['slot']], reference['references/'+ident+'/backbone'][:]):
                    raise ValueError('Covered native backbone differs')
            records.append(_record(path, m, native[0], item, 'native', 0, c['usalign']))
            native_done.add(ident)
    return records
