"""Exploratory training-label sensitivity; never changes frozen label sampling."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from summarize_ensemble import rmsd


def partition(ca, valid):
    parent = list(range(len(ca)))
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for i in range(len(ca)):
        for j in range(i):
            if valid[i] and valid[j] and rmsd(ca[i], ca[j]) <= 2:
                parent[find(i)] = find(j)
    return np.array([find(i) if valid[i] else -1 for i in range(len(ca))])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--labels', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    rows = []
    for path in a.labels:
        with h5py.File(path) as f:
            for ident, g in f.items():
                ca = g['teacher_backbone'][:, :, 1, :]
                valid = g['coarse_valid'][:].astype(bool)
                original = g['cluster'][:]
                rebuilt = partition(ca, valid)
                if not np.array_equal(original[:, None] == original[None], rebuilt[:, None] == rebuilt[None]):
                    raise ValueError('frozen all-residue clusters did not reproduce')
                confidence = g['teacher_plddt'][:]
                if not np.isfinite(confidence).all() or confidence.min() < 0 or confidence.max() > 1:
                    raise ValueError('expected confidence in [0,1]')
                row = dict(id=ident, length=ca.shape[1], all_residue_clusters=len(set(original) - {-1}),
                           valid_samples=int(valid.sum()))
                # Same mask for every conformation; exploratory threshold fixed before inspecting results.
                core = confidence[valid].mean(0) >= .7
                row['high_confidence_residues'] = int(core.sum())
                row['high_confidence_fraction'] = float(core.mean())
                row['high_confidence_clusters'] = len(set(partition(ca[:, core], valid)) - {-1}) if core.sum() >= 32 else None
                rows.append(row)
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate training target')
    comparable = [r for r in rows if r['high_confidence_clusters'] is not None]
    summary = dict(targets=len(rows), comparable=len(comparable),
                   mean_all_residue_clusters=float(np.mean([r['all_residue_clusters'] for r in comparable])),
                   mean_high_confidence_clusters=float(np.mean([r['high_confidence_clusters'] for r in comparable])),
                   fewer_clusters=sum(r['high_confidence_clusters'] < r['all_residue_clusters'] for r in comparable),
                   all_singletons=sum(r['all_residue_clusters'] == r['valid_samples'] for r in comparable),
                   core_singletons=sum(r['high_confidence_clusters'] == r['valid_samples'] for r in comparable),
                   mean_high_confidence_fraction=float(np.mean([r['high_confidence_fraction'] for r in rows])))
    result = dict(status='complete', protocol='2 A CA RMSD components, all residues versus mean teacher pLDDT >=0.7 shared mask; require32 core residues',
                  scope='Exploratory training-only label audit; not state truth, no label edits or checkpoint selection', summary=summary, rows=rows)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
