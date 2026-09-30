"""Score completed GPU predictions on CPU, accounting for every target/sample.

CA lDDT is the primary metric here. tm_after_kabsch is a diagnostic, not the
optimized TM-score used in the legacy report. No best-of-samples selection.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import time

import h5py
import numpy as np
from latentfold.metrics import ca_metrics


def score_one(payload):
    setting, name, sample_index, pred, ref, backbone = payload
    metrics = ca_metrics(pred, ref)
    if metrics['ca_lddt'] is None:
        raise ValueError(f'undefined CA lDDT: {name}')
    reference_short = np.linalg.norm(np.diff(ref, axis=0), axis=1) < 4.5
    predicted_ca = np.linalg.norm(np.diff(pred, axis=0), axis=1)
    peptide = np.linalg.norm(backbone[:-1, 2] - backbone[1:, 0], axis=1)
    return dict(setting=setting, target_id=name, sample=sample_index, length=len(ref), **metrics,
                reference_adjacent_short_count=int(reference_short.sum()),
                predicted_ca_gaps_on_reference_short=int(((predicted_ca > 4.5) & reference_short).sum()),
                peptide_length_outliers_on_reference_short=int((((peptide < 1.1) | (peptide > 1.6)) & reference_short).sum()))


def payloads(run, manifest):
    config = manifest['config']
    expected_ids = set(config['target_ids'])
    expected_settings = {f'steps{s}_cfg{g:g}' for s in config['flow_steps'] for g in config['guidance']}
    source = Path(manifest['source'])/'data/phase1_dataset/dataset_exp_val_esmc.h5'
    with h5py.File(source, 'r') as reference, h5py.File(run/'predictions.h5', 'r') as predictions:
        refs = {name: reference['val'][name]['ca_coords'][:] for name in expected_ids}
        if set(predictions) != expected_settings:
            raise ValueError('sampling settings do not match manifest')
        for setting in sorted(predictions):
            seen = set()
            for target in predictions[setting].values():
                name = target.attrs['target_id']
                if name in seen or name not in expected_ids:
                    raise ValueError('duplicate or unexpected target')
                seen.add(name)
                if set(target) != {str(i) for i in range(config['samples'])}:
                    raise ValueError('missing or extra samples')
                for k in range(config['samples']):
                    yield setting, name, k, target[str(k)]['ca'][:], refs[name], target[str(k)]['backbone'][:]
            if seen != expected_ids:
                raise ValueError('missing targets')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    a = parser.parse_args()
    if a.workers < 1:
        parser.error('workers must be positive')
    manifest = json.loads((a.run/'manifest.json').read_text())
    if manifest['status'] != 'complete':
        raise ValueError('refusing to summarize incomplete GPU run')
    started = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as workers:
        rows = list(workers.map(score_one, payloads(a.run, manifest), chunksize=8))
    if len(rows) != manifest['completed_predictions']:
        raise ValueError('score coverage differs from GPU run')
    summaries = {}
    for setting in sorted({r['setting'] for r in rows}):
        selected = [r for r in rows if r['setting'] == setting]
        summaries[setting] = dict(predictions=len(selected), targets=len({r['target_id'] for r in selected}),
            mean_ca_lddt=float(np.mean([r['ca_lddt'] for r in selected])),
            mean_ca_rmsd=float(np.mean([r['ca_rmsd'] for r in selected])),
            diagnostic_mean_tm_after_kabsch=float(np.mean([r['tm_after_kabsch'] for r in selected])))
    result = dict(status='complete', model=manifest['model'], coverage=1.0,
                  metric_note='CA lDDT; tm_after_kabsch is NOT optimized TM-score; all samples retained',
                  seconds=time.time()-started, summaries=summaries, records=rows)
    dest = a.run/'scores.json'
    if dest.exists():
        raise FileExistsError(dest)
    temp = dest.with_suffix('.tmp')
    temp.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    temp.replace(dest)
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
