"""Paired junction/geometry comparison; no sample or checkpoint selection."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from fragment_inpainting_core import audit
from fragment_junction_core import DRAW_KEYS, flank_bonds, connected_eligibility
from audit_inpainting_junctions import junctions
from extra_fragment_validation_core import load_conditions
from compare_extra_fragment_refolds import clustered
from prepare_overfit import sha


def compare(run, report):
    m = json.loads((run/'manifest.json').read_text()); d = json.loads(report.read_text())
    c = m['config']; audit(c)
    if (d['status'] != 'complete' or d['profile_only'] or not d.get('junction_weighted')
            or not d['numerically_qualified'] or d['manifest_sha256'] != sha(run/'manifest.json')
            or d['predictions_sha256'] != sha(run/'predictions.h5')
            or d['junction_protocol_sha256'] != sha(c['junction_protocol'])
            or d['refold_eligibility'] != connected_eligibility(d['records'])):
        raise ValueError('Complete audited fixed junction endpoint required')
    bm = json.loads(Path(c['junction_baseline_manifest']).read_text())
    bd = json.loads(Path(c['junction_baseline_report']).read_text())
    if len(m['training']) != 2000 or any(a[k] != b[k] for a, b in zip(m['training'], bm['training']) for k in DRAW_KEYS):
        raise ValueError('Unmatched2000update draws')
    ids = sorted({r['target_id'] for r in d['records']})
    items = load_conditions(c['fragments'], ids, 'c20_center', cohort='train')
    before = {(r['arm'], r['target_id'], r['generation_slot']): r for r in bd['records']}
    records = []
    with h5py.File(c['junction_baseline_predictions']) as f:
        for r in d['records']:
            key = (r['arm'], r['target_id'], r['generation_slot']); item = items[r['target_id']]
            bb = f[key[0]+'/'+key[1]+'/backbone'][key[2]]
            j = junctions(bb, item['start'], len(item['fragment']))
            flank = flank_bonds(bb, item['start'], len(item['fragment']), 4)
            old = before[key]
            records.append(dict(arm=key[0], target_id=key[1], slot=key[2],
                uniform=dict(junction_intact=j['valid'], connected_raw=old['raw_gate_passed'] and j['valid'],
                    coarse_valid=old['coarse_valid'], all_flank_edges_valid=flank['all_edges_valid'],
                    boundary_cn=j['peptide_distances'], flank_peptide_outliers=flank['peptide_outliers']),
                weighted=dict(junction_intact=r['junctions']['valid'], connected_raw=r['connected_raw'],
                    coarse_valid=r['coarse_valid'], all_flank_edges_valid=r['flank_bonds']['all_edges_valid'],
                    boundary_cn=r['junctions']['peptide_distances'], flank_peptide_outliers=r['flank_bonds']['peptide_outliers'])))
    summary, contrasts = [], []
    for arm in sorted({r['arm'] for r in records}):
        rr = [r for r in records if r['arm'] == arm]
        for mode in ('uniform', 'weighted'):
            summary.append(dict(arm=arm, objective=mode, samples=len(rr),
                **{k:sum(r[mode][k] for r in rr) for k in ('coarse_valid', 'junction_intact', 'connected_raw', 'all_flank_edges_valid', 'flank_peptide_outliers')},
                median_boundary_cn=float(np.median([v for r in rr for v in r[mode]['boundary_cn']]))))
        for metric in ('coarse_valid', 'junction_intact', 'connected_raw', 'all_flank_edges_valid'):
            contrasts.append(dict(arm=arm, metric=metric, weighted_minus_uniform=clustered([
                np.mean([int(r['weighted'][metric])-int(r['uniform'][metric]) for r in rr if r['target_id'] == ident]) for ident in ids])))
    return dict(status='complete', source_report_sha256=sha(report), baseline_report_sha256=sha(c['junction_baseline_report']),
        protocol_sha256=sha(c['junction_protocol']), manifest_sha256=sha(run/'manifest.json'),
        paired_updates=2000, prefix_max_abs=d['prefix_max_abs'], summary=summary, contrasts=contrasts,
        refold_eligibility=d['refold_eligibility'], records=records,
        scope='All128samples/arm,32training proteins; identical initialization and2000non-loss draws. Uniform and weighted '
              'training losses are different objectives and cannot be directly compared. No designability claim from geometry. '
              'Failure closes this fixed weighting recipe; no duration/window/weight sweep.')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--run', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True); p.add_argument('--output', type=Path, required=True); a=p.parse_args()
    d=compare(a.run, a.report); a.output.with_suffix('.json').write_text(json.dumps(d, indent=2)+'\n')
    lines=['# Junction-weighted versus uniform coordinate training', '', d['scope'], '',
           '|Arm|Loss|Coarse valid|Both junctions|Connected motif+geometry|All flank edges intact|Median boundary C–N Å|',
           '|---|---|---:|---:|---:|---:|---:|']
    for r in d['summary']:
        lines.append(f"|{r['arm']}|{r['objective']}|{r['coarse_valid']}|{r['junction_intact']}|{r['connected_raw']}|{r['all_flank_edges_valid']}|{r['median_boundary_cn']:.3f}|")
    lines += ['', 'All counts are out of128. Refold eligibility: '+str(d['refold_eligibility']), '',
              'Paired2000-update draws verified; profile/full first40 parameter max difference: '+str(d['prefix_max_abs'])+'.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(summary=d['summary'], refold_eligibility=d['refold_eligibility'])))


if __name__ == '__main__': main()
