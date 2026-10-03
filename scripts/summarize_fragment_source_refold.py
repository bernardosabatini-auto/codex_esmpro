"""Audit every source/design; motif, global and scaffold criteria share a refold."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from fragment_refinement_core import score_assay
from latentfold.metrics import usalign_coordinates
from prepare_fragment_source_refold import audit_inputs
from prepare_overfit import sha
from summarize_extra_fragment_refold import same_scaffold_success


def analyze(run):
    path = run/'manifest.json'
    manifest = json.loads(path.read_text())
    if manifest['status'] != 'complete':
        return dict(status=manifest['status'],error=manifest.get('error'))
    config = manifest['config']; audit_inputs(config)
    records = score_assay(run)
    with h5py.File(run/'refolded.h5') as folds, h5py.File(config['predictions']) as raw:
        for row in records:
            bb = raw[row['dataset']][0]
            mask = np.ones(row['length'], bool)
            mask[row['motif_start']:row['motif_start']+len(row['fixed_sequence'])] = False
            scores = [usalign_coordinates(config['usalign'],folds[row['name']+'/'+str(k)][:][mask,1],bb[mask,1]) for k in range(8)]
            passing = same_scaffold_success(row['successful_refold_indices'] if row['raw_gate_passed'] else [],scores)
            row.update(scaffold_scores=scores,scaffold_successful_refold_indices=passing,
                       scaffold_joint_success=bool(passing))
    summary = []
    for arm in ('original512','added7429'):
        rows = [r for r in records if r['arm']==arm]
        summary.append(dict(arm=arm,proteins=len(rows),designable=sum(r['valid_designable'] for r in rows),
                            strong_joint=sum(r['scaffold_joint_success'] for r in rows)))
    return dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),
                inventory_sha256=config['generation_manifest_sha256'],partition=config['partition'],
                completed_refolds=len(manifest['records']),summary=summary,records=records,
                elapsed_seconds=manifest['elapsed_seconds'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runs',type=Path,nargs=1,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=analyze(args.runs[0]);args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    view={k:v for k,v in report.items() if k!='records'}
    args.output.with_suffix('.md').write_text('# Training-source designability calibration\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')


if __name__=='__main__':
    main()
