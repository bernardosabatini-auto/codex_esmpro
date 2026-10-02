"""Independently audit the single-case replication and its saved controls."""
import argparse
import itertools
import json
from pathlib import Path

import h5py
import numpy as np

from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from latentfold.metrics import ca_metrics
from prepare_fragment_repetition import audit_config
from prepare_overfit import sha
from summarize_fragment_guidance import scaffold_rmsd


def analyze(run):
    path = run / 'manifest.json'
    m = json.loads(path.read_text()) if path.exists() else dict(status='failed', error='Missing manifest')
    if m['status'] != 'complete':
        return dict(status=m['status'], error=m.get('error'))
    c = m['config']
    audit_config(c)
    if m['training_updates'] or sha(run / 'predictions.h5') != m['predictions_sha256']:
        raise ValueError('Changed repetition output')
    expected = {('historical', 1), ('historical', 2), ('batch_partition', 1),
                ('batch_partition', 2), ('pose', 2)}
    if len(m['controls']) != 5 or {(r['kind'], r['guidance']) for r in m['controls']} != expected:
        raise ValueError('Missing controls')
    for r in m['controls']:
        if not np.isfinite(r['latent_max_abs']) or r['latent_max_abs'] > (1e-5 if r['kind'] == 'historical' else 1e-4):
            raise ValueError('Failed latent control')
        if r['kind'] == 'historical' and (r['max_ca_rmsd'] > .2 or r['min_ca_lddt'] < .99 or not r['same_validity']):
            raise ValueError('Failed historical geometry control')
    records, summaries = [], []
    with h5py.File(run / 'predictions.h5') as f, h5py.File(c['historical_predictions']) as old, h5py.File(c['fragments']) as fr:
        if set(f) != {'guidance1', 'guidance2', 'historical', 'controls'}:
            raise ValueError('Unexpected output inventory')
        v = fr['development/' + c['target_id']]
        q = v['conditions/' + c['condition']]
        fragment, start = q['fragment'][:], int(q.attrs['start'])
        for guidance in (1, 2):
            if set(f[f'guidance{guidance}']) != {c['target_id']}:
                raise ValueError('Changed replication family')
            g = f[f'guidance{guidance}/{c["target_id"]}']
            z, bb = g['latent'][:], g['backbone'][:]
            if bb.shape != (c['samples'], int(v.attrs['length']), 4, 3) or z.shape != (c['samples'], len(bb[0]), 8) or not np.isfinite(bb).all() or not np.isfinite(z).all():
                raise ValueError('Invalid generation arrays')
            if np.max(abs(z - f[f'controls/partition{guidance}'][:])) > 1e-4:
                raise ValueError('Stored partition parity failed')
            if guidance == 2 and np.max(abs(z - f['controls/pose2'][:])) > 1e-4:
                raise ValueError('Stored pose parity failed')
            history = f[f'historical/guidance{guidance}']
            reference = old[f'guidance{guidance}/{c["target_id"]}']
            if np.max(abs(history['latent'][:] - reference['latent'][:])) > 1e-5:
                raise ValueError('Stored historical latent mismatch')
            hb, rb = history['backbone'][:], reference['backbone'][:]
            if hb.shape != rb.shape or not np.array_equal(backbone_geometry(hb)['coarse_valid'], backbone_geometry(rb)['coarse_valid']):
                raise ValueError('Stored historical validity mismatch')
            for x, y in zip(hb, rb):
                score = ca_metrics(x[:, 1], y[:, 1])
                if score['ca_rmsd'] > .2 or score['ca_lddt'] < .99:
                    raise ValueError('Stored historical structure mismatch')
            valid = backbone_geometry(bb)['coarse_valid']
            rows = []
            for slot, x in enumerate(bb):
                fit = motif_fit(x, fragment, start)
                rows.append(dict(guidance=guidance, target_id=c['target_id'], family=str(v.attrs['family']),
                    slot=slot, coarse_valid=bool(valid[slot]),
                    strict_raw=bool(valid[slot] and fit['motif_drms'] <= 1 and fit['motif_ca_rmsd'] <= 1), **fit))
            records.extend(rows)
            keep = np.zeros(len(bb[0]), dtype=bool)
            keep[start:start+len(fragment)] = True
            pairs = [scaffold_rmsd(bb[i], bb[j], keep) for i, j in itertools.combinations(range(len(bb)), 2)
                     if rows[i]['strict_raw'] and rows[j]['strict_raw']]
            summaries.append(dict(guidance=guidance, samples=len(rows), valid=sum(r['coarse_valid'] for r in rows),
                strict_raw=sum(r['strict_raw'] for r in rows), mean_motif_ca_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rows])),
                raw_qualified_diversity_pairs=len(pairs), raw_qualified_scaffold_rmsd=float(np.mean(pairs)) if pairs else None))
    if len(m['batches']) != 2 or {r['guidance'] for r in m['batches']} != {1, 2}:
        raise ValueError('Missing timings')
    return dict(status='complete', manifest_sha256=sha(path), predictions_sha256=m['predictions_sha256'],
        summaries=summaries, records=records, controls=m['controls'], timing=m['batches'], elapsed_seconds=m['elapsed_seconds'],
        interpretation='Single selected development case, new fixed noise seed. Raw matches require refolding; this is not independent-protein validation.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=Path, nargs=1, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d = analyze(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2) + '\n')
    view = {k: v for k, v in d.items() if k != 'records'}
    a.output.with_suffix('.md').write_text('# Fragment noise replication\n\n```json\n' + json.dumps(view, indent=2) + '\n```\n')


if __name__ == '__main__':
    main()
