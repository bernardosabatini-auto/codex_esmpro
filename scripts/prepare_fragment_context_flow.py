"""CPU-only, family-separated isolated inputs and contextual supervision."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import h5py
import torch
from latentfold.fragment_context_flow import isolated_features
from prepare_overfit import sha


def family_split(rows, excluded, seed):
    eligible = [r for r in rows if r['family'] not in excluded]
    if len({r['family'] for r in rows}) != len(rows):
        raise ValueError('This pilot requires one protein per family')
    validation = set()
    for bucket in (128, 256, 384, 512):
        values = [r for r in eligible if r['bucket'] == bucket]
        values.sort(key=lambda r: hashlib.sha256(f'{seed}:{r["family"]}'.encode()).hexdigest())
        if len(values) < 5:
            raise ValueError('Insufficient training/validation families')
        validation.update(r['family'] for r in values[:4])
    return {r['id']: ('evaluation' if r['family'] in excluded else
                      'validation' if r['family'] in validation else 'train') for r in rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    torch.set_num_threads(1)
    root = Path(__file__).resolve().parents[1]
    protocol = root/'configs/fragment_context_flow_protocol.json'
    spec = json.loads(protocol.read_text())
    source, panel = root/spec['source'], root/spec['panel_manifest']
    pm = json.loads(panel.read_text())
    if pm['status'] != 'complete':
        raise ValueError('Incomplete historical panel')
    selected = pm['config']['selected']
    excluded = {r['family'] for r in selected}
    if len(selected) != 32 or len(excluded) != 32:
        raise ValueError('Incorrect fixed evaluation panel')
    a.output.mkdir(exist_ok=False)
    records = []; arrays = {}; max_pose = 0.
    with h5py.File(source) as f:
        rows = [dict(id=k, family=str(g.attrs['family']), length=len(g['reference_z']),
                     bucket=((len(g['reference_z'])+127)//128)*128) for k, g in f['train'].items()]
        split = family_split(rows, excluded, spec['seed'])
        for part in ('train', 'validation', 'evaluation'):
            feats = []; positions = []; targets = []
            for row in sorted(rows, key=lambda r: r['id']):
                if split[row['id']] != part:
                    continue
                g = f['train/'+row['id']]
                conditions = ['c20_center'] if part == 'evaluation' else spec['conditions']
                for condition in conditions:
                    q = g['conditions/'+condition]; start = int(q.attrs['start'])
                    latent = torch.from_numpy(q['latent'][:]); bb = torch.from_numpy(q['fragment'][:])
                    sequence = str(q.attrs['sequence'])
                    features, placement = isolated_features(latent, bb, sequence, length=row['length'], start=start)
                    # The frame, not the original full target, follows supplied coordinates.
                    rot = torch.tensor([[0., -1., 0.], [0., 0., 1.], [-1., 0., 0.]], dtype=torch.float64)
                    moved, moved_pos = isolated_features(latent, bb.double()@rot+13, sequence, length=row['length'], start=start)
                    gap = float((features-moved).abs().max()); max_pose = max(max_pose, gap)
                    if gap > 1e-5 or not torch.equal(placement, moved_pos):
                        raise ValueError('Isolated pose control failed')
                    feats.append(features.numpy()); positions.append(placement.numpy())
                    if part != 'evaluation':
                        target = g['reference_z'][start:start+20]
                        if target.shape != (20, 8) or not np.isfinite(target).all():
                            raise ValueError('Invalid context label')
                        targets.append(target)
                    records.append(dict(**row, split=part, condition=condition, start=start,
                                        sequence=sequence, index=len(feats)-1))
            arrays[part+'_features'] = np.stack(feats)
            arrays[part+'_placement'] = np.stack(positions)
            if targets:
                arrays[part+'_targets'] = np.stack(targets)
    # Only training labels set normalization. Evaluation targets are absent.
    arrays['mean'] = arrays['train_targets'].mean(axis=(0, 1), dtype=np.float64).astype(np.float32)
    arrays['std'] = arrays['train_targets'].std(axis=(0, 1), dtype=np.float64).astype(np.float32)
    if np.any(arrays['std'] < 1e-5) or any(not np.isfinite(x).all() for x in arrays.values()):
        raise ValueError('Nonfinite/degenerate export')
    counts = {s: len({r['family'] for r in records if r['split'] == s}) for s in ('train', 'validation', 'evaluation')}
    if counts != dict(train=464, validation=16, evaluation=32):
        raise ValueError('Unexpected split counts')
    path = a.output/'arrays.npz'
    with path.open('xb') as out:
        np.savez(out, **arrays)
    m = dict(status='complete', spec=spec, records=records, counts=counts,
             arrays=str(path.resolve()), arrays_sha256=sha(path), pose_max_abs=max_pose,
             sources=[dict(path=str(x.resolve()), sha256=sha(x)) for x in (source, panel, protocol)],
             no_evaluation_targets=True)
    (a.output/'manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    print(json.dumps(dict(counts=counts, conditions=len(records), pose_max_abs=max_pose, arrays_sha256=m['arrays_sha256'])))


if __name__ == '__main__':
    main()
