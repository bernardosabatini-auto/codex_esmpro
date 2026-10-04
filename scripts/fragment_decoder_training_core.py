"""Bound data, schedules and eligibility for direct coordinate conditioning."""
import json
from pathlib import Path
import h5py
import torch

from latentfold.fragment_decoder import DecoderFragmentAdapter
from masked_fragment_training_core import load_training as load_latents, panel
from fragment_preference_calibration import audit_generation
from prepare_overfit import sha


def audit(c):
    for r in c['sources']:
        if sha(r['path']) != r['sha256']:
            raise ValueError('Changed decoder-conditioning source: ' + r['path'])
    spec = json.loads(Path(c['protocol']).read_text())
    base = json.loads(Path(c['baseline_manifest']).read_text())
    bc = base['config']
    audit_generation(bc)
    report = json.loads(Path(c['baseline_report']).read_text())
    closed = json.loads(Path(c['closed_manifest']).read_text())
    cr = json.loads(Path(c['closed_report']).read_text())
    if (spec != c['spec'] or base['status'] != 'complete' or report['status'] != 'complete'
            or report['controls'] != 68 or report['manifest_sha256'] != sha(c['baseline_manifest'])
            or report['predictions_sha256'] != sha(c['baseline_predictions'])
            or Path(c['baseline_manifest']).parent.name != spec['baseline_generation']
            or c['selected'] != bc['selected'] or c['fragments'] != bc['fragments']
            or c['decoder_checkpoint'] != bc['decoder_checkpoint']
            or Path(bc['checkpoint']).parent.name != spec['parent']
            or Path(c['closed_manifest']).parent.name != spec['closed_clock_run']
            or closed['status'] != 'complete' or cr['status'] != 'complete' or cr['refold_gate']['qualified']
            or cr['manifest_sha256'] != sha(c['closed_manifest'])
            or c['training_ids'] != closed['config']['training_ids']
            or c['updates'] != spec['profile_updates' if c['profile_only'] else 'updates']):
        raise ValueError('Changed decoder experiment lineage')
    dm = json.loads(Path(c['diagnostic_manifest']).read_text())
    if (dm['status'] != 'complete' or dm['predictions_sha256'] != sha(c['diagnostic_predictions'])
            or dm['config']['baseline_predictions'] != c['baseline_predictions']):
        raise ValueError('Changed direct-native control source')
    with h5py.File(c['fragments']) as f:
        if sorted(f['train']) != c['training_ids'] or len(c['training_ids']) != 512:
            raise ValueError('Changed full training inventory')
    if not c['profile_only']:
        p = json.loads(Path(c['profile_report']).read_text())
        if (p['status'] != 'complete' or not p['profile_only'] or not p['qualified']
                or not p['fragment_decoder'] or p['protocol_sha256'] != sha(c['protocol'])
                or c['allocation_minutes'] != p['recommended_full_minutes'] or c['allocation_minutes'] > 150):
            raise ValueError('Unqualified direct decoder profile')
    return spec


def initial_adapter(c):
    return DecoderFragmentAdapter(seed=c['spec']['seed']).state_dict()


def canonical_frozen_state(model):
    state = model.frozen_state()
    result = {k.replace('cond_factory.base.', 'cond_factory.').replace('pair_repr_builder.base.', 'pair_repr_builder.'): v for k, v in state.items()}
    if len(result) != len(state):
        raise ValueError('Ambiguous decoder wrapper parameter mapping')
    return result


def expected_frozen_state(c):
    ck = torch.load(c['decoder_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
    return {k[len('decoder.'):]: v for k, v in ck['state_dict'].items() if k.startswith('decoder.')}


def load_training(c):
    data = load_latents(c)
    with h5py.File(c['fragments']) as f:
        for ident, row in data.items():
            bb = torch.from_numpy(f['train/' + ident + '/reference_backbone'][:])
            if bb.shape != (row['length'], 4, 3) or not torch.isfinite(bb).all():
                raise ValueError('Finite full native supervision required')
            row['backbone'] = bb
    return data


def training_batch(data, ident, names):
    r = data[ident]
    b, n = len(names), r['length']
    q = [r['conditions'][name] for name in names]
    return (r['target'][None].expand(b, -1, -1), r['backbone'][None].expand(b, -1, -1, -1),
            torch.stack([x['features'] for x in q]), torch.stack([x['keep'] for x in q]),
            torch.ones(b, n, dtype=torch.bool), torch.stack([x['coordinates'] for x in q]))


def refold_eligibility(summary, records, ids, spec):
    expected = {'parent', 'native_direct', 'generated_cond', 'generated_null', 'native_cond', 'native_null'}
    lookup = {r['arm']: r for r in summary}
    keys = {(r['arm'], r['target_id'], r['generation_slot']) for r in records}
    if (len(ids) != 32 or len(set(ids)) != 32 or set(lookup) != expected or len(summary) != 6
            or any(r['samples'] != 128 for r in summary) or len(records) != 768
            or keys != {(a, i, k) for a in expected for i in ids for k in range(4)}):
        raise ValueError('Complete full decoder diagnostic required')
    for arm in expected:
        rr = [r for r in records if r['arm'] == arm]
        if lookup[arm]['raw'] != sum(r['raw_gate_passed'] for r in rr) or lookup[arm]['valid'] != sum(r['coarse_valid'] for r in rr):
            raise ValueError('Decoder summaries disagree with recorded outcomes')
    if (lookup['parent']['raw'], lookup['parent']['valid'], lookup['native_direct']['raw'], lookup['native_direct']['valid']) != (25, 128, 128, 128):
        raise ValueError('Historical control changed')
    limits = spec['refold_eligibility']
    checks = dict(strict_success_still_possible=lookup['generated_cond']['raw'] >= limits['generated_cond_min_raw'],
                  designability_floor_still_possible=lookup['generated_cond']['valid'] >= limits['generated_cond_min_valid'])
    return dict(qualified=all(checks.values()), checks=checks,
                scope='Logical feasibility only. Actual same-valid-refold success and designability decide advancement.')
