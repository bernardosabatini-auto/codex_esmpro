"""Bind a decoded local-geometry objective to the matched full122 experiment."""
import argparse
import json
from pathlib import Path
import math
from prepare_overfit import sha
from expanded_corpus import metadata


def prepare(root, profile=None, minutes=None):
    protocol = root/'configs/local_geometry122_protocol.json'
    recipe = json.loads(protocol.read_text())
    c = json.loads((root/'runs/expanded_profile.json').read_text())
    metadata(c)
    c['local_geometry'] = recipe['local_geometry']
    for name in ('protocol', 'followup_protocol'):
        c[name] = str(protocol.resolve()); c[name+'_sha256'] = sha(protocol)
    if profile is None: return [c]
    report = json.loads(profile.read_text()); run = root/'runs'/profile.stem
    m = json.loads((run/'manifest.json').read_text())
    device = json.loads((run/'device_metadata.json').read_text())
    if report['status'] != 'complete' or not report['profile_only'] or report['max_reserved_gib'] > 80 or m['status'] != 'complete' or m['updates'] != 40 or m['config'] != c or 'RTX PRO 6000 Blackwell' not in device['cuda_device_name']:
        raise ValueError('failed or mismatched RTX profile')
    rows = m.get('local_geometry_updates', [])
    if len(rows) != 40 or {r['step'] for r in rows} != set(range(1, 41)):
        raise ValueError('incomplete gradient accounting')
    fields = ('flow_parameter_grad_norm', 'aux_parameter_grad_norm', 'effective_geometry_weight', 'aux_to_flow_ratio', 'geometry_loss')
    if any(not math.isfinite(r[k]) or r[k] < 0 for r in rows for k in fields) or any(r['flow_parameter_grad_norm'] <= 0 or r['aux_to_flow_ratio'] > .100001 for r in rows):
        raise ValueError('invalid gradient control')
    if {r['length'] for r in rows if r['aux_parameter_grad_norm'] > 0 and r['effective_geometry_weight'] > 0} != {128, 256, 384, 512}:
        raise ValueError('no nonzero auxiliary contribution in every bucket')
    if minutes is None or minutes < 10: raise ValueError('provide measured full runtime allocation')
    c.update(profile_only=False, updates=recipe['updates'], evaluation_steps=recipe['evaluation_steps'], work_cap_seconds=(minutes-6)*60, profile_report=str(profile.resolve()), profile_report_sha256=sha(profile))
    return [dict(c, seed=seed) for seed in recipe['seeds']]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', type=Path); p.add_argument('--minutes', type=int)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    for c in prepare(Path(__file__).resolve().parents[1], a.profile, a.minutes):
        out = a.output.with_name(f'{a.output.stem}_{c["seed"]}.json') if a.profile else a.output
        out.write_text(json.dumps(c, indent=2)+'\n'); print(out)


if __name__ == '__main__': main()
