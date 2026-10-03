"""Describe where completed same-refold assays fail, without combining refolds."""
import argparse
from collections import Counter
import json
from pathlib import Path

from prepare_overfit import sha


ARMS = ('control512', 'control_weight3', 'broad_weight3', 'control_frozen',
        'broad_frozen', 'control', 'quality')


def refold_stage(record):
    folds, scaffold = record['refolds'], record['scaffold_scores']
    if (len(folds) != 8 or len(scaffold) != 8
            or [r['sequence_index'] for r in folds] != list(range(8))):
        raise ValueError('Changed ordered eight-design budget')
    valid = {i for i, r in enumerate(folds) if r['coarse_valid']}
    global_ok = {i for i in valid if folds[i]['sc_tm'] > .5}
    motif_ok = {i for i in valid if folds[i]['motif_ca_rmsd'] <= 1 and folds[i]['motif_drms'] <= 1}
    joint = global_ok & motif_ok
    strong = {i for i in joint if scaffold[i] > .5}
    if sorted(joint) != record['successful_refold_indices'] or sorted(strong) != record['scaffold_successful_refold_indices']:
        raise ValueError('Saved same-refold decisions disagree')
    if not valid:
        stage = 'no_valid_refold'
    elif not global_ok:
        stage = 'no_valid_global_refold'
    elif not joint:
        stage = 'global_without_same_refold_motif'
    elif not strong:
        stage = 'joint_without_scaffold_agreement'
    else:
        stage = 'strong_success'
    return stage, bool(global_ok and motif_ok and not joint)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--comparisons', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    sources, screen, records = {}, {}, {}
    for comparison in a.comparisons:
        c = json.loads(comparison.read_text())
        if c['status'] != 'complete':
            raise ValueError('Incomplete comparison')
        sources[str(comparison)] = sha(comparison)
        for source in c['source_reports']:
            path = Path(source['path'])
            if sha(path) != source['sha256']:
                raise ValueError('Changed completed partition')
            d = json.loads(path.read_text())
            if d['status'] != 'complete':
                raise ValueError('Incomplete partition')
            sources[str(path)] = source['sha256']
            for field, inventory in (('screen_rows', screen), ('records', records)):
                for r in d[field]:
                    if r['arm'] not in ARMS:
                        continue
                    key = (r['arm'], r['target_id'], r['generation_slot'])
                    if key in inventory and inventory[key] != r:
                        raise ValueError('Conflicting reused sample')
                    inventory[key] = r
    summary = []
    for arm in ARMS:
        for cohort in ('all', 'short', 'long'):
            rows = [(k, r) for k, r in screen.items() if k[0] == arm and
                    (cohort == 'all' or (r['length'] <= 256) == (cohort == 'short'))]
            if len(rows) != (256 if cohort == 'all' else 128):
                raise ValueError('Incomplete generation denominator')
            counts = Counter(); split = 0
            for key, row in rows:
                if not row['raw_gate_passed']:
                    counts['failed_raw_screen'] += 1
                    continue
                if key not in records or not records[key]['raw_gate_passed']:
                    raise ValueError('Missing raw-match refolding')
                stage, split_attempts = refold_stage(records[key])
                counts[stage] += 1; split += split_attempts
            if sum(counts.values()) != len(rows):
                raise ValueError('Nonexclusive failure categories')
            summary.append(dict(arm=arm, cohort=cohort, generations=len(rows),
                                stages=dict(counts), different_refolds_pass_global_and_motif_only=split))
    scope = ('Posthoc diagnostic of completed development assays. Stages are exclusive and retain all generations. '
             'After raw screening, each stage requires the preceding gates in the same valid refold; failures '
             'in eight designs do not prove impossibility. Split-refold victories are counted separately and '
             'never promoted. Unevaluated raw failures are not assigned refold designability. No new attempts, '
             'training labels, selection, thresholds or current-experiment changes.')
    result = dict(status='complete', sources=sources, summary=summary, scope=scope)
    a.output.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    stages = ('failed_raw_screen', 'no_valid_refold', 'no_valid_global_refold',
              'global_without_same_refold_motif', 'joint_without_scaffold_agreement', 'strong_success')
    lines = ['# Same-refold failure stages', '', scope, '',
             '|Arm|Raw failure|No valid refold|No global agreement|Global but motif lost|Joint but scaffold fails|Strong|',
             '|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        if r['cohort'] == 'all':
            lines.append('|' + r['arm'] + '|' + '|'.join(str(r['stages'].get(k, 0)) for k in stages) + '|')
    a.output.with_suffix('.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps([r for r in summary if r['cohort'] == 'all']))


if __name__ == '__main__':
    main()
