"""Analyze every predeclared inference-noise replication of a fixed selector."""
import argparse
import json
from pathlib import Path

import numpy as np
from analyze_consensus import select, evaluate, digest
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores, hardware


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = dict(status='complete', runs={}, failures=[], inference_noise_replications=True, training_replications=False)
    per_run, seeds, clusters = [], set(), None
    for run in args.runs:
        try:
            manifest = json.loads((run/'manifest.json').read_text())
            if manifest['status'] != 'complete':
                raise ValueError(manifest.get('error', 'incomplete predictions'))
            config = manifest['config']; seed = config['seed']
            if seed in seeds:
                raise ValueError('duplicate replication seed')
            seeds.add(seed)
            reference = json.loads((Path(config['reference_run'])/'manifest.json').read_text())
            for key in ('checkpoint', 'dataset', 'decoder_checkpoint', 'precision'):
                if manifest[key] != reference[key]:
                    raise ValueError('changed reference '+key)
            for key in ('samples', 'target_ids', 'target_manifest_sha256', 'decoder_steps'):
                if config[key] != reference['config'][key]:
                    raise ValueError('changed reference '+key)
            protocol = Path(config['consensus_protocol']); cluster_path = Path(config['development_clusters'])
            if digest(protocol) != config['consensus_protocol_sha256'] or digest(cluster_path) != config['development_clusters_sha256']:
                raise ValueError('selection protocol or cluster map changed')
            clusters = json.loads(cluster_path.read_text())['clusters']
            choice_path = run/'consensus_choices.json'
            if not choice_path.exists():
                select(run, choice_path, protocol)
            selection = json.loads(choice_path.read_text())
            if selection['protocol_sha256'] != config['consensus_protocol_sha256']:
                raise ValueError('frozen choices use another protocol')
            output = args.output.parent/run.name
            evaluate(choice_path, cluster_path, output)
            summary = json.loads(output.with_suffix('.json').read_text())
            try:
                summary['hardware'] = hardware(Path(str(run)+'_nsight.sqlite'), manifest['batches'])
            except Exception as error:
                summary['hardware'] = dict(status='unavailable', error=str(error))
            result['runs'][run.name] = dict(seed=seed, **summary)
            scores = json.loads((run/'scores.json').read_text()); validate_scores(manifest, scores)
            ref_scores = json.loads((Path(config['reference_run'])/'scores.json').read_text())
            if scores['usalign'] != ref_scores['usalign']:
                raise ValueError('scoring protocol changed')
            by_target = {name:{} for name in clusters}
            for row in scores['records']:
                by_target[row['target_id']][row['sample']] = row
            per_run.append({metric:{name:dict(mean=float(np.mean([r[metric] for r in rows.values()])),
                selected=rows[selection['choices'][name]['sample']][metric]) for name, rows in by_target.items()}
                for metric in ('tm_fixed_reference', 'ca_lddt')})
        except Exception as error:
            result['failures'].append(dict(run=str(run), error=f'{type(error).__name__}: {error}'))
    if result['failures']:
        result['status'] = 'incomplete'
    elif len(per_run) == 2:
        result['replications_only_paired'] = {metric:paired_comparison(
            {name:float(np.mean([r[metric][name]['mean'] for r in per_run])) for name in clusters},
            {name:float(np.mean([r[metric][name]['selected'] for r in per_run])) for name in clusters}, clusters=clusters)
            for metric in ('tm_fixed_reference', 'ca_lddt')}
    lines = ['# Three-sample consensus: independent inference noise', '',
        'Same untouched checkpoint, frozen selection rule, all development targets. These vary inference noise, not training seeds or target population. The initial screen is excluded from the replication-only pooled comparison.', '',
        '| Inference seed | Mean TM | Selected TM | Selection gain [95% cluster CI] |', '|---:|---:|---:|---|']
    for row in result['runs'].values():
        paired = row['pairs']['tm_fixed_reference']['sample_mean']
        lines.append(f"| {row['seed']} | {paired['ours']:.5f} | {paired['theirs']:.5f} | {paired['theirs_minus_ours']:+.5f} {paired['ci95']} |")
    lines += ['', 'No independent-test scoring or accuracy promotion follows from this diagnostic alone.', '', '```json', json.dumps(result, indent=2), '```']
    args.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    main()
