"""CPU-only optimized TM scoring of both short-sampler arms and all checkpoints."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import h5py
import numpy as np
from latentfold.metrics import usalign_coordinates
from summarize_distillation_campaign import comparison


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', nargs="+", type=Path, required=True)
    p.add_argument('--usalign', type=Path, required=True)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); a.output.mkdir(exist_ok=False)
    metadata = json.loads((a.references / 'manifest.json').read_text())
    if metadata['status'] != 'complete' or metadata['split'] != 'tuning' or metadata['expected'] != 64:
        raise ValueError('verified tuning references required')
    ids = sorted(r['id'] for r in metadata['records'])
    if len(set(ids)) != 64 or len({r['family'] for r in metadata['records']}) != 64:
        raise ValueError('expected 64 independent families')
    binary = a.usalign.resolve(); references = {}
    with h5py.File(a.references / 'backbones.h5') as f:
        if set(f) != set(ids):
            raise ValueError('reference coverage mismatch')
        for ident in ids:
            references[ident] = f[ident]['backbone'][:, 1, :]
    result = dict(status='running', control='reflow_independent', rows=[], sources={}, binary_sha256=digest(binary),
                  arguments=['-TMscore', '1'], reference_manifest_sha256=digest(a.references / 'manifest.json'),
                  reference_array_sha256=digest(a.references / 'backbones.h5'),
                  scope='All 64 tuning families, three samples, both sampler arms, baseline25/CFG2 and 5/10-step CFG1 at 500/2000. No checkpoint selection or test scoring.')
    def save():
        temporary = a.output / 'score.tmp'; temporary.write_text(json.dumps(result, indent=2) + '\n')
        temporary.replace(a.output / 'score.json')
    save()
    try:
        arm_names = set()
        for run in a.runs:
            manifest = json.loads((run / 'manifest.json').read_text()); arm = manifest['config']['arm']
            if manifest['status'] != 'complete' or manifest['updates'] != 2000 or manifest['config']['selection_sha256'] != metadata['selection_sha256'] or arm in arm_names:
                raise ValueError('incomplete/unmatched training run')
            arm_names.add(arm)
            for step,n in [(0,25),(500,5),(500,10),(2000,5),(2000,10)]:
                path = run / f'evaluation_{step}_{n}.h5'; result['sources'][str(path)] = digest(path)
                tasks = []
                with h5py.File(path) as f:
                    if set(f) != set(ids):
                        raise ValueError('prediction coverage mismatch')
                    for ident in ids:
                        pred = f[ident][:]
                        if pred.shape != (3, len(references[ident]), 4, 3):
                            raise ValueError('prediction shape mismatch')
                        tasks.extend((ident, k, pred[k, :, 1]) for k in range(3))
                # Score every initial arm too: do not assume identical cross-device output.
                def score(task):
                    ident, k, pred = task
                    return dict(arm=arm, step=step, sampling_steps=n, target_id=ident, sample=k,
                                tm_fixed_reference=usalign_coordinates(binary, pred, references[ident]))
                with ThreadPoolExecutor(max_workers=2) as pool:
                    result['rows'].extend(pool.map(score, tasks))
                save(); print(arm, step, flush=True)
        expected = {'reflow_paired','reflow_independent'}
        if arm_names != expected:
            raise ValueError('incorrect experiment arms')
        values = {}
        for arm in sorted(arm_names):
            for step,n in [(0,25),(500,5),(500,10),(2000,5),(2000,10)]:
                values[arm, step, n] = [np.mean([r['tm_fixed_reference'] for r in result['rows'] if r['arm'] == arm and r['step'] == step and r['sampling_steps']==n and r['target_id'] == ident]) for ident in ids]
        result['comparisons'] = {arm: {f'{step}_{n}': {'initial': comparison(values[arm,step,n],values[arm,0,25]),
                                                      'matched_reference': comparison(values[arm,step,n],values['reflow_independent',step,n])}
                                                 for step,n in [(500,5),(500,10),(2000,5),(2000,10)]} for arm in sorted(arm_names)}
        result['status'] = 'complete'; save()
        lines = ['# Optimized fixed-correspondence TM accuracy', '', result['scope'], '',
                 'USalign optimizes the rigid fit while retaining the verified residue correspondence. AFDB reference structures are predictions. This supplements the separately reported Kabsch-based score; it does not replace or alter the state-coverage gate.', '',
                 '| Arm | Updates and steps | Mean TM | Change from own initialization | 95% family interval | Change from independent-noise control | 95% family interval |',
                 '|---|---:|---:|---:|---|---:|---|']
        for arm, steps in result['comparisons'].items():
            for step, metrics in steps.items():
                x, y = metrics['initial'], metrics['matched_reference']
                lines.append(f"| {arm} | {step} | {x['candidate_mean']:.5f} | {x['difference']:+.5f} | [{x['ci95'][0]:+.5f}, {x['ci95'][1]:+.5f}] | {y['difference']:+.5f} | [{y['ci95'][0]:+.5f}, {y['ci95'][1]:+.5f}] |")
        (a.output / 'score.md').write_text('\n'.join(lines) + '\n')
    except Exception as error:
        result.update(status='failed', error=repr(error)); save(); raise


if __name__ == '__main__':
    main()
