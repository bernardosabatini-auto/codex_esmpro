"""Localize the failed whole-chain pilot without changing its fixed gates."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np
import torch

from audit_masked_fragment_failure import analyze as localize
from extra_fragment_validation_core import load_conditions
from latentfold.masked_fragment_flow import editable_window
from pretrained_masked_refolding import require_clock_quality
from prepare_overfit import sha


def analyze(run, report):
    m = json.loads((run / 'manifest.json').read_text())
    d = json.loads(report.read_text())
    c = m['config']
    if not d.get('scaffold_clock'):
        raise ValueError('Expected the whole-chain clock experiment')
    result = localize(run, report)
    try:
        require_clock_quality(d, c['spec'])
    except ValueError:
        pass
    else:
        raise ValueError('Failed experiment admitted to refolding')
    # In this experiment every scaffold residue can change. The shared geometry
    # auditor's old fixed/editable names describe positions only; rename them.
    def rename(row):
        return {k.replace('fixed', 'scaffold').replace('editable', 'window'): v for k, v in row.items()}
    result['summary'] = [rename(r) for r in result['summary']]
    result['records'] = [rename(r) for r in result['records']]
    rows = {(r['arm'], r['target_id'], r['generation_slot']): r for r in d['records']}
    ids = [r['id'] for r in c['selected']]
    keys = [(i, k) for i in ids for k in range(4)]
    result['transitions'] = dict(
        retained_raw=sum(rows['parent', i, k]['raw_gate_passed'] and rows['generated_cond', i, k]['raw_gate_passed'] for i, k in keys),
        lost_raw=sum(rows['parent', i, k]['raw_gate_passed'] and not rows['generated_cond', i, k]['raw_gate_passed'] for i, k in keys),
        new_raw=sum(not rows['parent', i, k]['raw_gate_passed'] and rows['generated_cond', i, k]['raw_gate_passed'] for i, k in keys))
    items = load_conditions(c['fragments'], ids, 'c20_center', cohort='train')
    errors = []
    with h5py.File(run / 'predictions.h5') as f:
        for ident in ids:
            item = items[ident]
            window = editable_window(item['keep'][None], torch.ones(1, item['length'], dtype=torch.bool), c['spec']['flank'])[0].numpy()
            target = f['native_direct/' + ident + '/latent'][:]
            for arm in ('native_cond', 'native_null'):
                z = f[arm + '/' + ident + '/latent'][:]
                for slot in range(4):
                    errors.append(dict(arm=arm, target_id=ident, slot=slot,
                                       window_mse=float(np.mean((z[slot, window] - target[slot, window]) ** 2)),
                                       scaffold_mse=float(np.mean((z[slot, ~window] - target[slot, ~window]) ** 2))))
    result['native_endpoint_errors'] = [dict(arm=a, samples=128,
        mean_window_mse=float(np.mean([r['window_mse'] for r in errors if r['arm'] == a])),
        mean_scaffold_mse=float(np.mean([r['scaffold_mse'] for r in errors if r['arm'] == a]))) for a in ('native_cond', 'native_null')]
    result['native_endpoint_records'] = errors
    result['refold_export_rejects_failed_run'] = True
    result['protocol_sha256'] = sha(c['protocol'])
    result['scope'] = ('Post hoc localization on the same 32 repeatedly used training proteins, four draws each. '
        'Window means supplied motif plus eight flanking residues; scaffold means the remaining residues. '
        'All regions were free to move. Bond/clash/gap categories overlap. Native context is an oracle, '
        'not generated success. Transition counts are not a promoted selection policy. '
        'No designability was measured for this failed arm; all refold gates remain unchanged.')
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d = analyze(a.run, a.report)
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2) + '\n')
    visible = {k: v for k, v in d.items() if k not in ('records', 'native_endpoint_records')}
    a.output.with_suffix('.md').write_text('# Whole-chain adjustment failure diagnosis\n\n```json\n' + json.dumps(visible, indent=2) + '\n```\n')
    print(json.dumps(dict(transitions=d['transitions'], native_endpoint_errors=d['native_endpoint_errors'], summary=d['summary'])))


if __name__ == '__main__':
    main()
