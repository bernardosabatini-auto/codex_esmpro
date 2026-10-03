import argparse
import json
import math
from pathlib import Path

from broad_fragment_training import audit_broad
from prepare_overfit import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--arm', required=True)
    p.add_argument('--protocol', type=Path)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--profile', type=Path)
    p.add_argument('--matched-profile', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = (a.protocol or root / 'configs/fragment_broad_training_protocol.json').resolve()
    spec = json.loads(protocol.read_text())
    arm = spec['arms'][a.arm]
    parent = root / 'runs' / spec['parent']
    report = root / 'reports' / (parent.name + '.json')
    c = json.loads(report.read_text())['config'].copy()
    for k in ('profile_report', 'profile_report_sha256', 'allocation_minutes', 'latent_weight_profile_audit'):
        c.pop(k, None)
    data = a.data.resolve() / arm['corpus']
    dm = json.loads((data / 'manifest.json').read_text())
    c.update(extension_arm=a.arm, profile_only=a.profile is None, seed=spec['seed'],
             updates=40 if a.profile is None else spec['updates'],
             evaluation_steps=[40] if a.profile is None else spec['evaluation_steps'],
             total_prior_updates=spec['total_prior_updates'], work_cap_seconds=1110,
             allocation_minutes=20, corpus=arm['corpus'], motif_mass=arm['motif_mass'],
             training_protein_count=dm['training_protein_count'])
    if 'freeze_trunk' in arm:
        c['freeze_trunk'] = arm['freeze_trunk']
    for key, path in [('extension_protocol', protocol), ('broad_corpus_protocol', protocol),
                      ('warm_protocol', protocol), ('latent_weight_protocol', protocol),
                      ('warm_parent_manifest', parent / 'manifest.json'), ('warm_parent_report', report),
                      ('warm_predictions', parent / 'evaluation_2000.h5'), ('checkpoint', parent / 'ema_2000.ckpt'),
                      ('data_manifest', data / 'manifest.json'), ('data_report', data / 'report.json'),
                      ('fragments', data / 'fragments.h5'), ('expanded_protocol', root / spec['assembly_protocol'])]:
        c[key], c[key + '_sha256'] = str(path.resolve()), sha(path)
    if a.profile:
        if a.matched_profile is None:
            raise ValueError('Matched four-arm profile comparison is required')
        pd = json.loads(a.profile.read_text())
        overhead = max(0, pd['elapsed_seconds'] - pd['training_seconds'] - pd['evaluation_seconds'])
        estimate = pd['training_seconds'] / 40 * spec['updates'] + pd['evaluation_seconds'] / 2 * 12 * 3 + overhead + 300
        minutes = max(30, math.ceil((estimate * 1.2 + 120) / 60))
        c.update(profile_report=str(a.profile.resolve()), profile_report_sha256=sha(a.profile),
                 factorial_profile_report=str(a.matched_profile.resolve()), factorial_profile_report_sha256=sha(a.matched_profile),
                 allocation_minutes=minutes, work_cap_seconds=60 * minutes - 90)
    audit_broad(c)
    a.output.write_text(json.dumps(c, indent=2) + '\n')
    print(json.dumps(dict(arm=a.arm, proteins=c['training_protein_count'], allocation_minutes=c['allocation_minutes'])))


if __name__ == '__main__':
    main()
