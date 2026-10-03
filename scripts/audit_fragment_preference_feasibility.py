"""Retrospective training-only ranking diagnostic; no failed gate is relabeled."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np
import torch

from latentfold.fragment_preferences import split_preference
from prepare_overfit import sha


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); root = Path(__file__).resolve().parents[1]
    rp = root / 'reports/fragment_feedback_50080056.json'
    mp = root / 'runs/fragment_feedback_50080056/manifest.json'
    report, manifest = json.loads(rp.read_text()), json.loads(mp.read_text())
    c = manifest['config']
    if (report['status'] != 'complete' or manifest['status'] != 'complete'
            or report['manifest_sha256'] != sha(mp) or report['feedback_training_qualified']
            or report['completed_refolds'] != 192 or report['native_count'] != 8
            or report['refolded_sha256'] != sha(mp.parent / 'refolded.h5')):
        raise ValueError('Wrong completed failed feedback collection')
    sources = {str(p): sha(p) for p in (rp, mp, Path(c['fragments']))}
    if sources[c['fragments']] != c['fragments_sha256']:
        raise ValueError('Changed training fragments')
    generated = [r for r in report['records'] if r['mode'] == 'generated']
    ids = sorted({r['target_id'] for r in generated})
    if len(ids) != 8 or len(generated) != 16 or set(ids) != set(c['selected_training_ids']):
        raise ValueError('Changed feedback inventory')
    with h5py.File(c['fragments']) as f:
        if not set(ids) <= set(f['train']) or set(ids) & set(f['development']):
            raise ValueError('Not training-only')
        # Actual source has a single endpoint per condition. Permuting eight
        # copies of that endpoint cannot improve the noise/target coupling.
        costs = []
        for ident in ids:
            target = torch.from_numpy(f['train/' + ident + '/reference_z'][:]).double()
            noise = torch.randn((8, *target.shape), generator=torch.Generator().manual_seed(2026100402), dtype=torch.float64)
            targets = target[None].expand(8, -1, -1)
            before = (noise - targets).square().mean()
            after = (noise - targets.flip(0)).square().mean()
            costs.append(float(abs(before - after)))
    preferences = [split_preference([r for r in generated if r['target_id'] == ident]) for ident in ids]
    eligible = sum(r['eligible'] for r in preferences)
    confirmed = sum(r['confirmed'] for r in preferences)
    # Identity-flow counterexample: exact teacher trajectories with condition
    # sign(endpoint) have zero regression loss, yet fresh noise ignores the sign.
    generator = np.random.default_rng(2026100402)
    teacher_noise = generator.normal(size=100000)
    condition = teacher_noise > 0
    fresh_noise = generator.normal(size=len(condition))
    illustration = dict(teacher_endpoint_reconstruction_mse=0.,
                        condition_agreement_with_reused_noise=1.,
                        condition_agreement_with_fresh_noise=float(np.mean((fresh_noise > 0) == condition)))
    result = dict(status='complete', sources=sources, training_only=True,
                  original_feedback_training_gate=False, original_qualified_backbones=0,
                  retrospective_preferences=preferences, discovery_eligible=eligible,
                  split_confirmed=confirmed, max_within_condition_permutation_cost_change=max(costs),
                  identity_flow_counterexample=illustration,
                  scope='Retrospective exploration, not prospective label qualification or a training result. '
                  'Global/scaffold agreement remains hard and same-refold; motif error is graded only for ranking. '
                  'One endpoint per condition makes within-condition reassignment degenerate. Directly fitting '
                  'one noise per structure changes the conditional noise distribution; preserving teacher paths '
                  'does not by itself teach independent-noise conditioning. No inversion GPU experiment launched. '
                  'This does not rule out a conditional transport method that preserves the required marginals.',
                  decision='Insufficient confirmed protein coverage for preference training. Preserve the failed '
                  'binary-label collection. Any new collection must prospectively bind its source selection, '
                  'design split, minimum coverage and unchanged strict endpoint before generating labels.')
    a.output.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    view = {k: v for k, v in result.items() if k not in ('sources', 'retrospective_preferences')}
    a.output.with_suffix('.md').write_text('# Training-only preference and coupling audit\n\n```json\n' + json.dumps(view, indent=2) + '\n```\n')
    print(json.dumps(view))


if __name__ == '__main__': main()
