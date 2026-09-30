"""Freeze a reference-confidence weighting ablation using training inputs only.

The confidence signal is AFDB pLDDT, not a measured experimental error. Keep all
proteins and all residues. Normalize within each existing length bucket so that
changing confidence weights does not also change the expected bucket scale.
"""
import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
from latentfold.quality import confidence_weights
import torch


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--training-manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    data = json.loads(a.training_manifest.read_text())
    if data['status'] != 'complete':
        raise ValueError('training data incomplete')
    records = {}; raw_arrays = {}
    with h5py.File(data['dataset'], 'r') as h:
        if set(h['train']) != {r['id'] for r in data['records']}:
            raise ValueError('training ID coverage differs')
        for row in data['records']:
            g = h['train'][row['id']]
            confidence = g['plddt'][:].astype(np.float32)
            if confidence.shape != (row['length'],) or not np.isfinite(confidence).all() or np.any((confidence < 0) | (confidence > 100)):
                raise ValueError('missing or invalid source confidence')
            if abs(confidence.mean()-row['mean_plddt']) > 1e-4:
                raise ValueError('confidence differs from verified source manifest')
            raw = confidence_weights(torch.from_numpy(confidence)).numpy()
            raw_arrays[row['id']] = raw
            records[row['id']] = dict(bucket=row['bucket'], length=row['length'],
                sequence_sha256=row['sequence_sha256'], mean_plddt=float(confidence.mean()),
                confidence_array_sha256=hashlib.sha256(confidence.tobytes()).hexdigest(),
                raw_weight=float(raw.mean(dtype=np.float64)))
    summary = {}
    for bucket in sorted({r['bucket'] for r in records.values()}):
        group = [r for r in records.values() if r['bucket'] == bucket]
        raw = np.array([r['raw_weight'] for r in group]); scale = float(raw.mean())
        if scale <= 0:
            raise ValueError('zero-confidence bucket')
        for r in group:
            r['weight'] = r['raw_weight']/scale
        weights = raw/scale
        all_raw = np.concatenate([raw_arrays[n] for n, r in records.items() if r['bucket'] == bucket])
        summary[str(bucket)] = dict(count=len(group), mean_raw_weight=scale,
            weight_quantiles=np.quantile(weights, [0, .25, .5, .75, 1]).tolist(),
            residue_raw_weight_quantiles=np.quantile(all_raw, [0, .1, .25, .5, .75, 1]).tolist(),
            effective_sample_size=float(weights.sum()**2/np.square(weights).sum()),
            fraction_mean_plddt_below_80=float(np.mean([r['mean_plddt'] < 80 for r in group])))
    report = dict(status='complete', training_manifest=str(a.training_manifest.resolve()),
        training_manifest_sha256=hashlib.sha256(a.training_manifest.read_bytes()).hexdigest(),
        formula='clip((pLDDT-50)/40, 0.05, 1), divided by fixed mean_proteins(mean_residues(raw_weight)) within the training length bucket',
        reduction='mean_proteins(mean_residues(residue_weight * latent flow squared error)); no minibatch renormalization',
        scope='Training reference confidence only; no filtering, no model or development scores; every weight remains positive.',
        limitation='pLDDT measures predicted local reliability; it does not verify domain orientation or experimental correctness.',
        records=records, buckets=summary)
    if any(r['weight'] <= 0 for r in records.values()):
        raise ValueError('weighting would silently remove a training protein')
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
