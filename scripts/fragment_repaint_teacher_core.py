"""Lineage and scope for an oracle teacher, never an isolated-input claim."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit(c):
    from fragment_preference_calibration import audit_generation
    for source in c['sources']:
        if sha(source['path']) != source['sha256']:
            raise ValueError('Changed RePaint teacher source')
    spec = json.loads(Path(c['protocol']).read_text())
    base = json.loads(Path(c['baseline_manifest']).read_text())
    report = json.loads(Path(c['baseline_report']).read_text())
    historical = json.loads(Path(c['historical_manifest']).read_text())
    hr = json.loads(Path(c['historical_report']).read_text())
    bc, hc = base['config'], historical['config']
    audit_generation(bc)
    if (spec != c['spec'] or Path(c['baseline_manifest']).parent.name != spec['baseline_generation']
            or Path(c['historical_manifest']).parent.name != spec['historical_generation']
            or base['status'] != 'complete' or report['status'] != 'complete' or report['controls'] != 68
            or report['manifest_sha256'] != sha(c['baseline_manifest'])
            or report['predictions_sha256'] != sha(c['baseline_predictions'])
            or historical['status'] != 'complete' or hr['status'] != 'complete'
            or hc['checkpoint'] != c['checkpoint'] or sha(c['checkpoint']) != hc['checkpoint_sha256']
            or hc['decoder_checkpoint'] != c['decoder_checkpoint'] or bc['decoder_checkpoint'] != c['decoder_checkpoint']
            or c['historical_predictions'] != str(Path(c['historical_manifest']).parent/'predictions.h5')
            or c['historical_selection'] != hc['selection'] or c['historical_parent_predictions'] != hc['parent_predictions']
            or c['fragments'] != bc['fragments'] or c['selected'] != bc['selected'] or c['target_ids'] != bc['target_ids']
            or c['native_sources'] != bc['native_sources'] or c['arm'] != 'oracle_repaint'
            or tuple(spec[k] for k in ('condition','targets','samples','steps','repaint','decoder_steps','seed'))
                != ('c20_center',32,4,50,3,3,2026100405)
            or c['allocation_minutes'] != 15 or c['work_cap_seconds'] != 780
            or spec['allocation_minutes'] != 15 or spec['work_cap_seconds'] != 780):
        raise ValueError('Changed oracle teacher recipe or population')
    return spec


def eligibility(rows):
    if len(rows) != 128 or len({(r['target_id'],r['generation_slot']) for r in rows}) != 128:
        raise ValueError('All128 teacher outputs required')
    return dict(raw=sum(r['raw_gate_passed'] for r in rows),valid=sum(r['coarse_valid'] for r in rows),
                qualified=sum(r['raw_gate_passed'] for r in rows)>=9 and sum(r['coarse_valid'] for r in rows)>=45)
