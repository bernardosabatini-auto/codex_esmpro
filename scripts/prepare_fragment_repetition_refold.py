"""Keep the full fresh-noise denominator and refold every passing raw sample."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from prepare_fragment_repetition import audit_config
from prepare_overfit import sha


def screen(c):
    for key in ('generation_manifest', 'generation_report', 'generation_predictions', 'protocol', 'fragments'):
        if sha(c[key]) != c[key + '_sha256']:
            raise ValueError('Changed replication screening source: ' + key)
    m = json.loads(Path(c['generation_manifest']).read_text())
    d = json.loads(Path(c['generation_report']).read_text())
    gc = m['config']
    audit_config(gc)
    if m['status'] != 'complete' or d['status'] != 'complete' or d['manifest_sha256'] != c['generation_manifest_sha256'] or m['predictions_sha256'] != c['generation_predictions_sha256'] or gc['fragments_sha256'] != c['fragments_sha256'] or gc['protocol_sha256'] != c['protocol_sha256']:
        raise ValueError('Unaudited replication source')
    rows, selected = [], {}
    with h5py.File(c['generation_predictions']) as pred, h5py.File(c['fragments']) as fr:
        ident = gc['target_id']
        g = fr['development/' + ident]
        q = g['conditions/' + gc['condition']]
        item = (q['fragment'][:], str(q.attrs['sequence']), int(q.attrs['start']), str(g.attrs['family']))
        for guidance in gc['guidance']:
            arm = f'guidance{guidance}'
            if set(pred[arm]) != {ident}:
                raise ValueError('Changed single-case inventory')
            bb = pred[arm + '/' + ident + '/backbone'][:]
            if bb.shape != (gc['samples'], int(g.attrs['length']), 4, 3) or not np.isfinite(bb).all():
                raise ValueError('Changed fresh sample inventory')
            valid = backbone_geometry(bb)['coarse_valid']
            for slot, x in enumerate(bb):
                fit = motif_fit(x, item[0], item[2])
                passed = bool(valid[slot] and fit['motif_drms'] <= 1 and fit['motif_ca_rmsd'] <= 1)
                rows.append(dict(arm=arm, target_id=ident, family=item[3], generation_slot=slot,
                    length=len(x), raw_gate_passed=passed, coarse_valid=bool(valid[slot]), **fit))
                if passed:
                    selected[arm, ident, slot] = (x, *item)
    return rows, selected, item


def audit_inputs(c, check_teacher=True):
    for key in ('predictions', 'usalign', 'native_predictions'):
        if sha(c[key]) != c[key + '_sha256']:
            raise ValueError('Changed replication refold source')
    if check_teacher:
        for r in c['dependencies'] + c['teacher_artifacts']:
            if sha(r['path']) != r['sha256']:
                raise ValueError('Changed teacher artifact')
    spec = json.loads(Path(c['protocol']).read_text())
    rows, selected, item = screen(c)
    if rows != c['screen_rows'] or len(rows) != 2 * spec['samples']:
        raise ValueError('Changed complete denominator')
    if c['screens'] != [{'arm': f'guidance{g}'} for g in spec['guidance']]:
        raise ValueError('Changed arm inventory')
    wanted = set(selected) | {('native', spec['target_id'], 0)}
    if not 1 <= len(wanted) <= spec['max_refold_backbones'] or c['expected_backbones'] != len(wanted) or len(c['entries']) != len(wanted) or {(r['arm'], r['target_id'], r['generation_slot']) for r in c['entries']} != wanted:
        raise ValueError('Dropped or added raw match/native control')
    train = json.loads(Path(json.loads(Path(c['generation_manifest']).read_text())['config']['generation_manifest']).read_text())
    if c['native_predictions_sha256'] != train['config']['initial_predictions_sha256']:
        raise ValueError('Unregistered native source')
    with h5py.File(c['predictions']) as out, h5py.File(c['native_predictions']) as native:
        if set(out) != {'motifs'} | {r['dataset'] for r in c['entries']}:
            raise ValueError('Unexpected raw input groups')
        if set(out['motifs']) != {spec['target_id']}:
            raise ValueError('Unexpected motif groups')
        for r in c['entries']:
            bb = native['references/' + r['target_id'] + '/backbone'][:] if r['arm'] == 'native' else selected[r['arm'], r['target_id'], r['generation_slot']][0]
            if r['slot'] != 0 or r['length'] != len(bb) or r['family'] != item[3] or r['fixed_sequence'] != item[1] or r['fixed_start'] != item[2] or r['motif_start'] != item[2] or r['repeatability_control'] != (r['arm'] == 'native'):
                raise ValueError('Changed fixed motif or native control')
            if not np.array_equal(out[r['dataset']][:], bb[None]) or not np.array_equal(out['motifs/' + r['target_id']][:], item[0]):
                raise ValueError('Changed raw/native arrays')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--generation', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    run = a.generation.resolve()
    m = json.loads((run / 'manifest.json').read_text())
    prior = json.loads((root / 'runs/fragment_strict_followup_49989126/manifest.json').read_text())['config']
    c = {k: prior[k] for k in ('num_sequences', 'temperature', 'mpnn_seed', 'seed',
                             'mpnn', 'dependencies', 'teacher_artifacts', 'precision', 'usalign', 'usalign_sha256')}
    c.update(assay='fragment_repetition_refold', screens=[{'arm': 'guidance1'}, {'arm': 'guidance2'}], work_cap_seconds=720)
    for key, path in [('generation_manifest', run / 'manifest.json'),
                      ('generation_report', root / 'reports' / (run.name + '.json')),
                      ('generation_predictions', run / 'predictions.h5'),
                      ('protocol', Path(m['config']['protocol'])), ('fragments', Path(m['config']['fragments']))]:
        c[key], c[key + '_sha256'] = str(path), sha(path)
    c['screen_rows'], selected, item = screen(c)
    ident = m['config']['target_id']
    train = json.loads(Path(m['config']['generation_manifest']).read_text())
    nativepath = Path(train['config']['initial_predictions'])
    inputs = a.output.with_suffix('.h5').resolve()
    entries = []
    with h5py.File(inputs, 'x') as out, h5py.File(nativepath) as native:
        out.create_dataset('motifs/' + ident, data=item[0])
        for arm, i, slot in [('native', ident, 0)] + sorted(selected):
            bb = native['references/' + i + '/backbone'][:] if arm == 'native' else selected[arm, i, slot][0]
            name = f'repetition_{arm}_{slot:02d}'
            out.create_dataset(name, data=bb[None])
            entries.append(dict(name=name, head=arm, arm=arm, mode='native' if arm == 'native' else 'generated',
                target_id=i, family=item[3], generation_slot=slot, slot=0, length=len(bb), dataset=name,
                motif_start=item[2], fixed_start=item[2], fixed_sequence=item[1], repeatability_control=arm == 'native'))
    c.update(entries=entries, expected_backbones=len(entries))
    for key, path in [('predictions', inputs), ('native_predictions', nativepath)]:
        c[key], c[key + '_sha256'] = str(path), sha(path)
    audit_inputs(c,check_teacher=False)
    a.output.write_text(json.dumps(c, indent=2) + '\n')
    print('Screened', len(c['screen_rows']), 'fresh outputs;', len(selected), 'raw matches;', len(entries)*8, 'refolds including native control')


if __name__ == '__main__':
    main()
