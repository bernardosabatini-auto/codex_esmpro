"""Independently audit adapter checkpoints and every direct-decoder output."""
import argparse
import json
import math
from pathlib import Path

import h5py
import numpy as np
import torch

from fragment_decoder_training_core import (audit, initial_adapter, expected_frozen_state,
    load_training, training_batch, panel, refold_eligibility)
from native_anchor_training_core import state_hash, tensor_hash
from extra_fragment_validation_core import load_conditions
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from latentfold.metrics import ca_metrics
from compare_extra_fragment_refolds import clustered
from prepare_overfit import sha


def analyze(run):
    mp = run/'manifest.json'
    m = json.loads(mp.read_text()) if mp.exists() else dict(status='failed', error='Missing manifest')
    if m['status'] != 'complete':
        return dict(status=m['status'], error=m.get('error'))
    c, spec = m['config'], audit(m['config'])
    selected, data = panel(c), load_training(c)
    ids = [r['id'] for r in selected]
    if (m['updates'] != c['updates'] or len(m['training']) != c['updates'] or m['peak_reserved_GiB'] > 75
            or len(m['controls']) != 6*len(ids) or len(m['evaluations']) != 4*len(ids)
            or m['checkpoint_sha256'] != sha(run/'checkpoint.pt') or m['predictions_sha256'] != sha(run/'predictions.h5')
            or m['initial_masked_sha256'] != sha(run/'initial_masked.h5') or m['initial_clean_sha256'] != sha(run/'initial_clean.h5')
            or len(m['initial_controls']) != 2*len(ids)+8 or len(m['checkpoint_replay']) != 2):
        raise ValueError('Incomplete decoder run or changed saved outputs')
    expected = expected_frozen_state(c)
    if not expected or state_hash(expected) != m['frozen_original'] or not (m['frozen_original'] == m['frozen_initial'] == m['frozen_final']):
        raise ValueError('Changed original decoder weights')
    del expected
    ck = torch.load(run/'checkpoint.pt', map_location='cpu', weights_only=True)
    initial = initial_adapter(c)
    if (ck['config'] != c or m['initial_adapter_sha256'] != state_hash(initial)
            or set(initial) != set(ck['raw']) or set(initial) != set(ck['ema'])
            or state_hash(ck['raw']) != m['final_adapter_sha256'] or state_hash(ck['ema']) != m['evaluated_adapter_sha256']
            or m['initial_adapter_sha256'] == m['final_adapter_sha256']
            or any(not torch.isfinite(v).all() for mode in ('raw', 'ema') for v in ck[mode].values())
            or any(not torch.equal(initial['centers'], ck[mode]['centers']) for mode in ('raw', 'ema'))):
        raise ValueError('Changed adapter initialization, checkpoint or fixed radial bases')
    gc = m['gradient_control']
    if (gc['prediction_tolerance_ratio'] > 1 or gc['gradient_tolerance_ratio'] > 1
            or gc['token_gradient_norm'] <= 0 or gc['pair_gradient_norm'] <= 0
            or not all(math.isfinite(x) for x in [*gc['losses'], gc['token_gradient_norm'], gc['pair_gradient_norm'], gc['gradient_max_abs'], gc['prediction_max_abs'], gc['prediction_tolerance_ratio'], gc['gradient_tolerance_ratio']])
            or not math.isclose(*gc['losses'], abs_tol=1e-4, rel_tol=1e-4)):
        raise ValueError('Invalid real-decoder gradient/checkpoint controls')
    order = np.random.default_rng(spec['seed'])
    buckets = {b: sorted(i for i, r in data.items() if r['bucket'] == b) for b in (128, 256, 384, 512)}
    for step, r in enumerate(m['training']):
        bucket = (128, 256, 384, 512)[step % 4]
        batch = spec['batches'][str(bucket)]
        ident = str(order.choice(buckets[bucket]))
        names = order.choice(spec['conditions'], size=batch).tolist()
        z, target, *_ = training_batch(data, ident, names)
        factor = min((step+1)/spec['warmup_updates'], 1)*(.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
        if (r['step'] != step+1 or r['bucket'] != bucket or r['batch'] != batch or r['length'] != data[ident]['length']
                or r['target_id'] != ident or r['conditions'] != names or r['learning_rate_factor'] != factor
                or r['context_sha256'] != tensor_hash(z) or r['target_sha256'] != tensor_hash(target)
                or not all(math.isfinite(r[k]) for k in ('loss', 'gradient_norm', 'position_mse', 'bond_mse'))
                or r['gradient_norm'] <= 0 or min(r['position_mse'], r['bond_mse']) < 0
                or not math.isclose(r['loss'], r['position_mse']+r['bond_mse'], rel_tol=1e-6, abs_tol=1e-6)):
            raise ValueError('Changed exact-length data/noise/optimizer schedule')
    prefix_error = None
    if not c['profile_only']:
        pm = json.loads(Path(c['profile_manifest']).read_text())
        keys = ('step', 'bucket', 'length', 'batch', 'target_id', 'conditions', 'learning_rate_factor',
                'context_sha256', 'target_sha256', 'noise_sha256')
        if (pm['initial_adapter_sha256'] != m['initial_adapter_sha256'] or len(pm['training']) != 40
                or any(x[k] != y[k] for x, y in zip(pm['training'], m['training'][:40]) for k in keys)
                or m['prefix_sha256'] != sha(run/'prefix_40.pt')):
            raise ValueError('Unmatched profile/full prefix')
        before = torch.load(c['profile_checkpoint'], map_location='cpu', weights_only=True)
        prefix = torch.load(run/'prefix_40.pt', map_location='cpu', weights_only=True)
        if any(set(prefix[mode]) != set(before[mode]) for mode in ('raw', 'ema')):
            raise ValueError('Changed prefix inventory')
        prefix_error = max(float((prefix[mode][k]-before[mode][k]).abs().max()) for mode in ('raw', 'ema') for k in prefix[mode])
        if prefix_error > 1e-4:
            raise ValueError('Profile/full adapter prefix diverged')
    items = load_conditions(c['fragments'], ids, 'c20_center', cohort='train')
    initial_ids = [next(r['id'] for r in c['selected'] if r['bucket'] == b) for b in (128, 256, 384, 512)]
    initial_keys = {(i, kind+'_masked') for i in ids for kind in ('generated', 'native')} | {(i, kind+'_clean') for i in initial_ids for kind in ('generated', 'native')}
    control_keys = {(i, kind) for i in ids for kind in ('parent', 'native_direct', 'generated_null_initial', 'native_null_initial', 'generated_cond_pose', 'native_cond_pose')}
    if ({(r['target_id'], r['kind']) for r in m['initial_controls']} != initial_keys
            or {(r['target_id'], r['kind']) for r in m['controls']} != control_keys
            or {(r['target_id'], r['arm']) for r in m['evaluations']} != {(i, a) for i in ids for a in ('generated_cond', 'generated_null', 'native_cond', 'native_null')}):
        raise ValueError('Changed decoder control inventory')
    records, replay = [], []
    arms = ('parent', 'native_direct', 'generated_cond', 'generated_null', 'native_cond', 'native_null')
    with h5py.File(run/'predictions.h5') as f, h5py.File(run/'initial_masked.h5') as initial, \
            h5py.File(run/'initial_clean.h5') as clean, h5py.File(c['baseline_predictions']) as old, \
            h5py.File(c['diagnostic_predictions']) as native:
        if set(f) != set(arms) or any(set(f[a]) != set(ids) for a in arms):
            raise ValueError('Changed evaluation denominator')
        if (set(initial) != {'generated', 'native'} or set(clean) != {'generated', 'native'}
                or any(set(initial[k]) != set(ids) or set(clean[k]) != set(initial_ids) for k in ('generated', 'native'))):
            raise ValueError('Changed initial masked/control denominator')
        for source in selected:
            ident, item = source['id'], items[source['id']]
            n, keep = item['length'], item['keep'].numpy()
            source_z = dict(generated=old['new/'+ident+'/latent'][:], native=np.repeat(data[ident]['target'].numpy()[None], 4, axis=0))
            references = dict(generated=old['new/'+ident+'/backbone'][:], native=native['native/'+ident+'/backbone'][:4])
            for kind in ('generated', 'native'):
                g = initial[kind+'/'+ident]
                z = source_z[kind].copy()
                z[:, keep] = 0
                error = float(np.max(abs(g['backbone'][:]-g['original_backbone'][:])))
                logged = next(r for r in m['initial_controls'] if (r['target_id'], r['kind']) == (ident, kind+'_masked'))
                if (not np.array_equal(z, g['latent'][:]) or g['backbone'].shape != (4, n, 4, 3)
                        or not np.isfinite(g['backbone'][:]).all() or not math.isfinite(error) or error > 1e-5 or error != logged['backbone_max_abs']):
                    raise ValueError('Changed zero-adapter masked control')
                if ident in initial_ids:
                    g = clean[kind+'/'+ident]
                    error = float(np.max(abs(g['backbone'][:]-g['original_backbone'][:])))
                    logged = next(r for r in m['initial_controls'] if (r['target_id'], r['kind']) == (ident, kind+'_clean'))
                    scores = check_backbones(g['backbone'][:], references[kind], item['fragment'], item['start'], ident)
                    if not math.isfinite(error) or error > 1e-5 or error != logged['backbone_max_abs'] or any(scores[k] != logged[k] for k in scores):
                        raise ValueError('Changed initial clean decoder parity')
            for arm in arms:
                kind = 'native' if arm.startswith('native') else 'generated'
                g = f[arm+'/'+ident]
                z, bb = g['latent'][:], g['backbone'][:]
                expected_z = source_z[kind].copy()
                if arm not in ('parent', 'native_direct'):
                    expected_z[:, keep] = 0
                if (z.shape != (4, n, 8) or bb.shape != (4, n, 4, 3) or not np.array_equal(z, expected_z)
                        or not np.isfinite(bb).all()):
                    raise ValueError('Changed hidden-motif decoder inputs or invalid outputs')
                if arm in ('parent', 'native_direct'):
                    scores = check_backbones(bb, references[kind], item['fragment'], item['start'], ident)
                    logged = next(r for r in m['controls'] if (r['target_id'], r['kind']) == (ident, arm))
                    if any(scores[k] != logged[k] for k in scores):
                        raise ValueError('Changed original frozen decoding')
                elif arm.endswith('_null'):
                    error = float(np.max(abs(bb-initial[kind+'/'+ident+'/backbone'][:])))
                    logged = next(r for r in m['controls'] if (r['target_id'], r['kind']) == (ident, arm+'_initial'))
                    if error > 1e-5 or error != logged['backbone_max_abs']:
                        raise ValueError('Condition-off output changed')
                else:
                    error = float(np.max(abs(bb-g['pose_backbone'][:])))
                    logged = next(r for r in m['controls'] if (r['target_id'], r['kind']) == (ident, arm+'_pose'))
                    if not math.isfinite(error) or error > 1e-4 or error != logged['backbone_max_abs']:
                        raise ValueError('Changed decoder fragment pose result')
                    if ident == ids[0]:
                        error = float(np.max(abs(bb-g['reloaded_backbone'][:])))
                        logged = next(r for r in m['checkpoint_replay'] if (r['target_id'], r['arm']) == (ident, arm))
                        if not math.isfinite(error) or error > 1e-5 or error != logged['backbone_max_abs']:
                            raise ValueError('Saved decoder EMA replay differs')
                        replay.append(logged)
                rr = raw_rows(bb, item['fragment'], item['start'], arm, ident, item['family'])
                for k, r in enumerate(rr):
                    scores = ca_metrics(bb[k, ~keep, 1], references[kind][k, ~keep, 1])
                    records.append(dict(r, bucket=source['bucket'], scaffold_ca_rmsd=scores['ca_rmsd']))
    summary = []
    for arm in arms:
        rr = [r for r in records if r['arm'] == arm]
        summary.append(dict(arm=arm, samples=len(rr), raw=sum(r['raw_gate_passed'] for r in rr),
            valid=sum(r['coarse_valid'] for r in rr), mean_motif_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])),
            mean_scaffold_rmsd=float(np.mean([r['scaffold_ca_rmsd'] for r in rr]))))
    eligibility = None if c['profile_only'] else refold_eligibility(summary, records, ids, spec)
    contrasts = []
    if not c['profile_only']:
        lookup = {(r['arm'], r['target_id'], r['generation_slot']): r for r in records}
        for candidate, reference in [('generated_cond', 'parent'), ('generated_cond', 'generated_null'), ('native_cond', 'native_null')]:
            metrics = {metric: clustered([np.mean([float(lookup[candidate, i, k][metric])-float(lookup[reference, i, k][metric]) for k in range(4)]) for i in ids])
                       for metric in ('raw_gate_passed', 'coarse_valid', 'motif_ca_rmsd')}
            contrasts.append(dict(candidate=candidate, reference=reference, metrics=metrics))
    recommended = max(10, math.ceil((m['training_seconds']*spec['updates']/c['updates']*1.5 +
        (m['elapsed_seconds']-m['training_seconds'])*10 + 120)/60)) if c['profile_only'] else None
    qualified = recommended <= 150 if c['profile_only'] else eligibility['qualified']
    return dict(status='complete', fragment_decoder=True, profile_only=c['profile_only'], numerically_qualified=True,
        qualified=qualified, manifest_path=str(mp.resolve()), manifest_sha256=sha(mp), protocol_sha256=sha(c['protocol']),
        fragments_sha256=sha(c['fragments']), checkpoint_sha256=m['checkpoint_sha256'], predictions_sha256=m['predictions_sha256'],
        updates=c['updates'], trainable_parameters=m['trainable_parameters'], training_seconds=m['training_seconds'],
        elapsed_seconds=m['elapsed_seconds'], peak_reserved_GiB=m['peak_reserved_GiB'], controls=len(m['controls']),
        initial_controls=len(m['initial_controls']), gradient_control=gc, saved_ema_gpu_replay=replay, prefix_max_abs=prefix_error,
        recommended_full_minutes=recommended, summary=summary, refold_eligibility=eligibility, contrasts=contrasts, records=records,
        scope='Repeated training-only diagnostic. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. '
              'Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=Path, nargs=1, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    torch.set_num_threads(1)
    d = analyze(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2)+'\n')
    visible = {k: v for k, v in d.items() if k != 'records'}
    a.output.with_suffix('.md').write_text('# Explicit fragment-conditioned coordinate decoder\n\n```json\n'+json.dumps(visible, indent=2)+'\n```\n')
    print(json.dumps(visible))


if __name__ == '__main__':
    main()
