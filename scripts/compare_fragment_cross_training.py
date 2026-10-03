"""Audit the two routing arms before profiling or interpreting their outcomes."""
import argparse
import json
from pathlib import Path

from broad_fragment_training import audit_broad
from compare_broad_fragment_training import initial_parity
from fragment_cross_training import compare_cross_traces
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=Path, nargs=2, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = root / 'configs/fragment_cross_training_protocol.json'
    manifests, reports, runs, sources = {}, {}, {}, []
    for run in a.runs:
        run = run.resolve()
        mp, rp = run / 'manifest.json', root / 'reports' / (run.name + '.json')
        m, d = json.loads(mp.read_text()), json.loads(rp.read_text())
        c = m['config']; arm = c['extension_arm']
        audit_broad(c)
        if (m['status'] != 'complete' or d['status'] != 'complete'
                or c != d['config'] or d['manifest_sha256'] != sha(mp)
                or c['broad_corpus_protocol_sha256'] != sha(protocol)
                or arm in manifests or c['profile_only'] and not d['profile_qualified']):
            raise ValueError('Unaudited routing arm')
        manifests[arm], reports[arm], runs[arm] = m, d, run
        sources.append(dict(arm=arm, run=str(run), manifest_sha256=sha(mp), report_sha256=sha(rp)))
    if len({m['config']['profile_only'] for m in manifests.values()}) != 1:
        raise ValueError('Mixed profile/full comparison')
    configs = [m['config'] for m in manifests.values()]
    exceptions = {'extension_arm', 'fragment_cross_attention', 'profile_report',
                  'profile_report_sha256', 'allocation_minutes', 'work_cap_seconds'}
    if any(configs[0].get(k) != configs[1].get(k) for k in set(configs[0]) | set(configs[1]) if k not in exceptions):
        raise ValueError('Unmatched training recipes')
    updates = compare_cross_traces(manifests)
    initial = {arm: initial_parity(runs['motif'] / 'evaluation_0.h5', run / 'evaluation_0.h5')
               for arm, run in runs.items()}
    result = dict(status='complete', profile_only=configs[0]['profile_only'],
                  protocol_sha256=sha(protocol), matched_training_updates=updates,
                  initial_predictions=initial, sources=sources,
                  arms={arm: {k: d[k] for k in ('training_seconds', 'evaluation_seconds', 'elapsed_seconds',
                                               'max_reserved_GiB', 'total_training_updates', 'summaries')}
                        for arm, d in reports.items()},
                  scope='Same frozen6000parent and adapter; equal new parameters, memory and random draws. Only cross-attention output routing differs. Technical checks do not establish designability.')
    atomic_json(a.output.with_suffix('.json'), result)
    view = {k: v for k, v in result.items() if k != 'arms'}
    a.output.with_suffix('.md').write_text('# Dynamic fragment routing audit\n\n```json\n' + json.dumps(view, indent=2) + '\n```\n')
    print(json.dumps({k: result[k] for k in ('status', 'matched_training_updates', 'initial_predictions')}))


if __name__ == '__main__':
    main()
