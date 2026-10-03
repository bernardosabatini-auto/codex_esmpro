"""Assemble qualified shards into matched corpora without choosing new targets."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from broad_fragment_full_core import gates, verify_original
from prepare_overfit import sha
from profile_gpu import atomic_json


def equal_group(a, b):
    if dict(a.attrs) != dict(b.attrs) or set(a) != set(b):
        raise ValueError('Changed copied group metadata')
    for key in a:
        if isinstance(a[key], h5py.Group):
            equal_group(a[key], b[key])
        elif not np.array_equal(a[key][:], b[key][:]):
            raise ValueError('Changed copied dataset')


def audit_shards(runs, root):
    shards = []
    seen = set()
    for run in runs:
        mp = run / 'manifest.json'
        rp = root / 'reports' / (run.name + '.json')
        m, report = json.loads(mp.read_text()), json.loads(rp.read_text())
        c = m['config']
        if (m['status'] != 'complete' or report['status'] != 'complete'
                or not report['data_gate_passed'] or report['manifest_sha256'] != sha(mp)
                or report['fragments_sha256'] != m['fragments_sha256']
                or sha(run / 'fragments.h5') != m['fragments_sha256']):
            raise ValueError('Unqualified data shard')
        result = gates(m['records'])
        if not result['data_gate_passed'] or any(report[k] != v for k, v in result.items()):
            raise ValueError('Changed shard qualification')
        ids = {r['target_id'] for r in m['records']}
        if ids & seen:
            raise ValueError('Overlapping shard targets')
        seen |= ids
        shards.append((run, m, report, dict(manifest=str(mp), manifest_sha256=sha(mp),
                      report=str(rp), report_sha256=sha(rp),
                      fragments=str(run / 'fragments.h5'), fragments_sha256=m['fragments_sha256'])))
    if len(shards) != 4 or {m['config']['partition'] for _, m, _, _ in shards} != set(range(4)):
        raise ValueError('All four disjoint partitions required')
    first = shards[0][1]['config']
    for _, m, _, _ in shards:
        for key in ('protocol', 'candidates', 'base_manifest', 'base_fragments', 'decoder_checkpoint'):
            if m['config'][key + '_sha256'] != first[key + '_sha256'] or sha(first[key]) != first[key + '_sha256']:
                raise ValueError('Changed shared corpus source')
    if len(seen) != 8192:
        raise ValueError('Incomplete candidate ledger')
    return shards, first


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=Path, nargs=4, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    shards, c = audit_shards([r.resolve() for r in a.runs], root)
    base = json.loads(Path(c['base_manifest']).read_text())
    candidates = json.loads(Path(c['candidates']).read_text())
    metadata = {r['id']: {k: r[k] for k in ('id', 'family', 'sequence', 'length', 'bucket')}
                for r in base['config']['training_targets'] + candidates['selected']}
    old_ids = {r['id'] for r in base['config']['training_targets']}
    records = [r for _, m, _, _ in shards for r in m['records']]
    accepted = {r['target_id'] for r in records if r['qualified']}
    if len(old_ids) != 512 or not old_ids <= accepted or not 7424 <= len(accepted) <= 8192:
        raise ValueError('Invalid qualified corpus size')
    a.output.mkdir(exist_ok=False)
    provenance = dict(shards=[s for _, _, _, s in shards], base_manifest=c['base_manifest'],
                      base_manifest_sha256=c['base_manifest_sha256'], base_fragments=c['base_fragments'],
                      base_fragments_sha256=c['base_fragments_sha256'],
                      candidates=c['candidates'], candidates_sha256=c['candidates_sha256'],
                      protocol=c['protocol'], protocol_sha256=c['protocol_sha256'])
    for name, ids in [('control512', old_ids), ('broad', accepted)]:
        outdir = a.output / name
        outdir.mkdir()
        with h5py.File(outdir / 'fragments.h5', 'x') as dest, h5py.File(c['base_fragments']) as old:
            dest.create_group('train')
            old.copy(old['development'], dest, name='development')
            equal_group(old['development'], dest['development'])
            if len(dest['development']) != 16:
                raise ValueError('Changed development cohort')
            for run, m, _, _ in shards:
                with h5py.File(run / 'fragments.h5') as source:
                    expected = {r['target_id'] for r in m['records'] if r['qualified']}
                    if set(source['train']) != expected:
                        raise ValueError('Changed retained source inventory')
                    for ident in sorted(expected & ids):
                        source.copy(source['train/' + ident], dest['train'], name=ident)
                        equal_group(source['train/' + ident], dest['train/' + ident])
                        if ident in old_ids:
                            verify_original(old['train/' + ident], dest['train/' + ident])
            if set(dest['train']) != ids or set(dest['train']) & set(dest['development']):
                raise ValueError('Changed assembled cohort')
        manifest = dict(status='complete', corpus=name, training_gate_passed=True,
                        training_protein_count=len(ids), fragments_sha256=sha(outdir / 'fragments.h5'),
                        config=dict(**provenance, training_targets=[metadata[i] for i in sorted(ids)],
                                    development_rows=base['config']['development_rows']),
                        excluded_new_ids=sorted(set(metadata) - accepted),
                        original_proteins_preserved=512, development_proteins_preserved=16,
                        conditions_per_training_protein=12)
        atomic_json(outdir / 'manifest.json', manifest)
        report = {k: v for k, v in manifest.items() if k not in ('config', 'excluded_new_ids')}
        report.update(manifest_sha256=sha(outdir / 'manifest.json'), rejected_new_proteins=8192-len(accepted))
        atomic_json(outdir / 'report.json', report)
        print(json.dumps(report))


if __name__ == '__main__':
    main()
