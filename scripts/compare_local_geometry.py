"""Paired two-seed capacity check for direct decoded geometry training."""
import argparse
import json
from pathlib import Path
import numpy as np
from compare_tail import matched, METRICS
from compare_overfit_balanced import scored
from latentfold.teacher_states import paired_change


def compare(full, candidates, step):
    recipe = json.loads(Path(candidates[0]['config']['protocol']).read_text()); seeds = recipe['seeds']
    if len(full) != 2 or len(candidates) != 2 or len(set(seeds)) != 2 or {m['config']['seed'] for m in full} != set(seeds) or {m['config']['seed'] for m in candidates} != set(seeds):
        raise ValueError('both declared seeds required')
    d = dict(step=step, matched=True, seeds=seeds, summaries={}, comparisons={}, capacity_retained={})
    for seed in seeds:
        f = next(m for m in full if m['config']['seed'] == seed)
        c = next(m for m in candidates if m['config']['seed'] == seed)
        targets, families, inventory, initial = matched(f, c, step, intervention='local_geometry')
        values = dict(full=scored(f, step, 1, targets), geometry=scored(c, step, 1, targets), initial=initial)
        cohorts = dict(all122=set(targets), original32=set(inventory['capacity_ids']), additional90=set(targets)-set(inventory['capacity_ids']))
        for cohort, ids in cohorts.items():
            for arm, rows in values.items():
                d['summaries'][f'{seed}_{arm}_{cohort}'] = {k:float(np.mean([rows[i][k] for i in sorted(ids)])) for k in METRICS}
            for reference in ('full','initial'):
                d['comparisons'][f'{seed}_geometry_{cohort}_vs_{reference}'] = {k:paired_change({i:values['geometry'][i][k] for i in ids}, {i:values[reference][i][k] for i in ids}, families={i:families[i] for i in ids}) for k in METRICS}
        r = d['comparisons'][f'{seed}_geometry_all122_vs_full']
        d['capacity_retained'][str(seed)] = r['coverage32']['ci95'][0] > -.05 and r['valid_fraction']['difference'] >= -.01
    d['replicated_capacity_retained'] = all(d['capacity_retained'].values())
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full', nargs=2, type=Path, required=True); p.add_argument('--candidate', nargs=2, type=Path, required=True)
    p.add_argument('--step', type=int, required=True); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    d = compare(*[[json.loads((r/'manifest.json').read_text()) for r in paths] for paths in (a.full,a.candidate)], a.step)
    lines = ['# Direct decoded geometry: matched training capacity', '', f'Checkpoint{a.step}. Both declared seeds, all122 training families. Initialization, schedules, data draws, protocol hashes and auxiliary gradient limits checked. No native or biological-state claim.', '', '| Seed / arm / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |', '|---|---:|---:|---:|---:|---:|']
    for name,r in d['summaries'].items(): lines.append(f"| {name} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
    for name,r in d['comparisons'].items():
        if 'all122' in name: lines += ['', f"{name}: recall delta{r['coverage32']['difference']:+.5f},95% interval{r['coverage32']['ci95']}; validity delta{r['valid_fraction']['difference']:+.5f}."]
    lines += ['', f"Capacity retained in both seeds under fixed5-point recall/1-point validity margins: {d['replicated_capacity_retained']}. These practical margins do not establish identical distributions. Native and external gates remain required."]
    a.output.with_suffix('.json').write_text(json.dumps(d, indent=2)+'\n'); a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__': main()
