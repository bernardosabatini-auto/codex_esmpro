"""Training-only AFDB confidence audit; never selects by evaluation outcomes."""
import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from latentfold.metrics import ca_metrics
from prepare_holdout import AA
from prepare_overfit import sha
from profile_gpu import atomic_json


def read_ca(path, sequence):
    letters, confidence, coordinates, residue_ids = [], [], [], []
    for line in path.read_text().splitlines():
        if line.startswith('ENDMDL'):
            break
        if line.startswith('ATOM') and line[12:16].strip() == 'CA' and line[16] in (' ', 'A'):
            letters.append(AA.get(line[17:20].strip(), 'X'))
            confidence.append(float(line[60:66]))
            coordinates.append([float(line[j:j+8]) for j in (30, 38, 46)])
            residue_ids.append(line[21:27])
    confidence = np.asarray(confidence)
    if ''.join(letters) != sequence or len(set(residue_ids)) != len(sequence):
        raise ValueError('Source sequence or residue mapping changed')
    if not np.isfinite(confidence).all() or np.any((confidence < 0) | (confidence > 100)):
        raise ValueError('Invalid AFDB confidence')
    return np.asarray(coordinates), confidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    broad = root/'runs/broad_fragment_corpora_20261003/broad'
    original = root/'runs/fragment_data_49981806/manifest.json'
    manifest = json.loads((broad/'manifest.json').read_text())
    old = {r['id']: r for r in json.loads(original.read_text())['config']['training_targets']}
    sources = {}
    for directory in sorted((root/'runs').glob('*/source_pdb')):
        for path in directory.glob('AF-*.pdb'):
            sources.setdefault(path.stem, path)
    records = []
    with h5py.File(broad/'fragments.h5') as f:
        for row in manifest['config']['training_targets']:
            ident = row['id']
            path = sources[ident]
            ca, confidence = read_ca(path, row['sequence'])
            error = ca_metrics(ca, f['train/'+ident+'/reference_backbone'][:, 1])['ca_rmsd']
            if error > .02:
                raise ValueError('Source coordinate disagreement: '+ident)
            start = (len(confidence)-20)//2
            records.append(dict(id=ident, cohort='original512' if ident in old else 'added7429',
                                bucket=row['bucket'], length=row['length'], source_pdb=str(path),
                                source_sha256=sha(path), source_ca_rmsd=error,
                                afdb_mean_plddt=float(confidence.mean()),
                                afdb_fraction_below70=float((confidence < 70).mean()),
                                afdb_center20_mean_plddt=float(confidence[start:start+20].mean()),
                                mean_teacher_confidence=old.get(ident, {}).get('mean_teacher_confidence')))
    summary = []
    for cohort in ('original512', 'added7429'):
        for bucket in (None, 128, 256, 384, 512):
            rows = [r for r in records if r['cohort'] == cohort and (bucket is None or r['bucket'] == bucket)]
            summary.append(dict(cohort=cohort, bucket=bucket, proteins=len(rows),
                                mean_plddt_median=float(np.median([r['afdb_mean_plddt'] for r in rows])),
                                mean_plddt_ge80=sum(r['afdb_mean_plddt'] >= 80 for r in rows),
                                mean_plddt_ge90=sum(r['afdb_mean_plddt'] >= 90 for r in rows),
                                fraction_below70_median=float(np.median([r['afdb_fraction_below70'] for r in rows]))))
    report = dict(status='complete', sources={str(p):sha(p) for p in (original, broad/'manifest.json', Path(__file__))},
                  scope='Training-only, all sources accounted for. AFDB pLDDT is distinct from the original ESMFold teacher-confidence filter; neither establishes designability.',
                  summary=summary, records=records)
    if args.output.exists():
        raise FileExistsError(args.output)
    atomic_json(args.output, report)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
