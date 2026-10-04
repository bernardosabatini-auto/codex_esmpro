"""Prospective junction-weighted objective: matched draws and connected outputs."""
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha
from audit_inpainting_junctions import junctions
from extra_fragment_validation_core import load_conditions


DRAW_KEYS = ('step', 'bucket', 'length', 'batch', 'target_id', 'conditions',
             'learning_rate_factor', 'context_sha256', 'target_sha256',
             'noise_sha256', 'time_sha256', 'dropout_sha256', 'times', 'dropped')


def audit_sources(c):
    js = json.loads(Path(c['junction_protocol']).read_text())
    m = json.loads(Path(c['junction_baseline_manifest']).read_text())
    r = json.loads(Path(c['junction_baseline_report']).read_text())
    comparison = json.loads(Path(c['junction_comparison']).read_text())
    diagnostic = json.loads(Path(c['junction_diagnostic']).read_text())
    if (js != c['junction_spec'] or c['junction_loss'] != {'junction_width': 4, 'junction_mass': .5}
            or any(c['junction_loss'][k] != js[k] for k in c['junction_loss'])
            or any(js[k] != c['spec'][k] for k in ('seed', 'sampling_seed', 'profile_updates', 'updates'))
            or Path(c['junction_baseline_manifest']).parent.name != js['baseline_training']
            or m['status'] != 'complete' or r['status'] != 'complete' or r['profile_only']
            or not r['numerically_qualified'] or not r['fragment_inpainting']
            or r['manifest_sha256'] != sha(c['junction_baseline_manifest'])
            or r['predictions_sha256'] != sha(c['junction_baseline_predictions'])
            or comparison['status'] != 'complete' or comparison['development_screen_qualified'] != {'generated_cond': False}
            or diagnostic['status'] != 'complete' or diagnostic['ten_step_followup_eligible'] is not False
            or any(c[k] != m['config'][k] for k in ('spec', 'selected', 'training_ids', 'protocol',
                       'baseline_manifest', 'baseline_predictions', 'diagnostic_manifest',
                       'diagnostic_predictions', 'fragments', 'decoder_checkpoint'))):
        raise ValueError('Changed junction objective, baseline, or failed prerequisites')
    bound = {r['path'] for r in c['sources']}
    if any(c[k] not in bound for k in ('junction_protocol', 'junction_baseline_manifest',
               'junction_baseline_predictions', 'junction_baseline_report', 'junction_comparison', 'junction_diagnostic')):
        raise ValueError('Unbound junction evidence')
    if not c['profile_only']:
        p = json.loads(Path(c['profile_report']).read_text())
        if not p.get('junction_weighted') or p['junction_protocol_sha256'] != sha(c['junction_protocol']):
            raise ValueError('Matching junction-weighted profile required')


def flank_bonds(bb, start, length, width):
    """Save every within-residue and peptide bond touching a weighted flank.

    Peptide/CA thresholds are the unchanged junction criteria. Intramolecular
    distances are descriptive, without inventing a new threshold after results.
    """
    residues = list(range(max(0, start-width), start)) + list(range(start+length, min(len(bb), start+length+width)))
    edges = sorted({i for r in residues for i in (r-1, r) if 0 <= i < len(bb)-1})
    cn = np.array([np.linalg.norm(bb[i, 2]-bb[i+1, 0]) for i in edges])
    ca = np.array([np.linalg.norm(bb[i, 1]-bb[i+1, 1]) for i in edges])
    return dict(residues=residues, edges=edges, peptide_distances=cn.tolist(), ca_distances=ca.tolist(),
        peptide_outliers=int(((cn < 1.1) | (cn > 1.6)).sum()), ca_gaps=int((ca > 4.5).sum()),
        all_edges_valid=bool(((cn >= 1.1) & (cn <= 1.6) & (ca <= 4.5)).all()),
        n_ca=np.linalg.norm(bb[residues, 0]-bb[residues, 1], axis=-1).tolist(),
        ca_c=np.linalg.norm(bb[residues, 1]-bb[residues, 2], axis=-1).tolist(),
        c_o=np.linalg.norm(bb[residues, 2]-bb[residues, 3], axis=-1).tolist())


def connected_eligibility(records):
    rows = [r for r in records if r['arm'] == 'generated_cond']
    if len(rows) != 128 or len({(r['target_id'], r['generation_slot']) for r in rows}) != 128:
        raise ValueError('Exactly128 unfiltered generated outputs required')
    count = sum(r['raw_gate_passed'] and r['junctions']['valid'] for r in rows)
    return dict(qualified=count >= 45, connected_raw=count, required=45)


def augment_report(d, run, m):
    c = m['config']
    baseline = json.loads(Path(c['junction_baseline_manifest']).read_text())
    if (baseline['initial_model_sha256'] != m['initial_model_sha256']
            or any(a[k] != b[k] for a, b in zip(m['training'], baseline['training']) for k in DRAW_KEYS)):
        raise ValueError('Changed initialization or paired baseline draws')
    if not c['profile_only']:
        profile = json.loads(Path(c['profile_manifest']).read_text())
        if profile['training'] != m['training'][:40] or d['prefix_max_abs'] != 0:
            raise ValueError('Junction profile/full first40 records and weights must match exactly')
    ids = sorted({r['target_id'] for r in d['records']})
    items = load_conditions(c['fragments'], ids, 'c20_center', cohort='train')
    controls = ('parent', 'native_direct', 'generated_untrained', 'native_untrained')
    with h5py.File(run/'predictions.h5') as new, h5py.File(c['junction_baseline_predictions']) as old:
        for arm in controls:
            for ident in ids:
                for name in ('latent', 'backbone'):
                    key = arm+'/'+ident+'/'+name
                    if not np.array_equal(new[key][:], old[key][:]):
                        raise ValueError('Historical untrained or original output changed: '+key)
        for r in d['records']:
            item = items[r['target_id']]
            bb = new[r['arm']+'/'+r['target_id']+'/backbone'][r['generation_slot']]
            r['junctions'] = junctions(bb, item['start'], len(item['fragment']))
            r['flank_bonds'] = flank_bonds(bb, item['start'], len(item['fragment']), 4)
            r['connected_raw'] = r['raw_gate_passed'] and r['junctions']['valid']
    for s in d['summary']:
        rows = [r for r in d['records'] if r['arm'] == s['arm']]
        s.update(junction_intact=sum(r['junctions']['valid'] for r in rows),
                 connected_raw=sum(r['connected_raw'] for r in rows),
                 all_flank_edges_valid=sum(r['flank_bonds']['all_edges_valid'] for r in rows),
                 flank_peptide_outliers=sum(r['flank_bonds']['peptide_outliers'] for r in rows),
                 flank_ca_gaps=sum(r['flank_bonds']['ca_gaps'] for r in rows))
    d.update(junction_weighted=True, junction_protocol_sha256=sha(c['junction_protocol']),
             paired_baseline_updates=len(m['training']), exact_control_replays=4*len(ids)*4,
             baseline_manifest_sha256=sha(c['junction_baseline_manifest']),
             legacy_refold_eligibility=d['refold_eligibility'])
    if not c['profile_only']:
        d['refold_eligibility'] = connected_eligibility(d['records'])
        d['qualified'] = d['refold_eligibility']['qualified']
    d['scope'] = ('Training-only junction-weighted fixed2000-update experiment. All original controls and untrained clamp '
                  'outputs match the uniform-loss baseline exactly; every training draw is paired. Raw motif retention is '
                  'imposed. Advancement requires45coarse-valid, motif-retaining backbones with intact junctions before '
                  'the unchanged8-design/refold budget. Same-refold motif/global/scaffold AND junction agreement is required. '
                  'Flank bond distances expose defects displaced outside the motif; geometry alone is not designability.')
    return d
