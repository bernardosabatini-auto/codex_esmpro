import argparse
import json
from pathlib import Path
from fragment_decoder_training_core import audit
from prepare_overfit import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--profile', action='store_true')
    p.add_argument('--profile-report', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = root / 'configs/fragment_decoder_protocol.json'
    spec = json.loads(protocol.read_text())
    base = root / 'runs' / spec['baseline_generation']
    closed = root / 'runs' / spec['closed_clock_run']
    bc = json.loads((base / 'manifest.json').read_text())['config']
    cc = json.loads((closed / 'manifest.json').read_text())['config']
    c = dict(spec=spec, profile_only=a.profile, updates=spec['profile_updates' if a.profile else 'updates'],
             selected=bc['selected'], training_ids=cc['training_ids'], sources=[], allocation_minutes=25, work_cap_seconds=1380)
    def bind(path):
        path = Path(path).resolve()
        c['sources'].append(dict(path=str(path), sha256=sha(path)))
        return str(path)
    for key, path in [('protocol', protocol), ('baseline_manifest', base/'manifest.json'),
                      ('baseline_report', root/'reports'/(base.name+'.json')), ('baseline_predictions', base/'predictions.h5'),
                      ('closed_manifest', closed/'manifest.json'), ('closed_report', root/'reports'/(closed.name+'.json')),
                      ('fragments', bc['fragments']), ('decoder_checkpoint', bc['decoder_checkpoint']),
                      ('diagnostic_manifest', cc['diagnostic_manifest']), ('diagnostic_predictions', cc['diagnostic_predictions'])]:
        c[key] = bind(path)
    if not a.profile:
        if a.profile_report is None:
            raise ValueError('Completed profile required')
        c['profile_report'] = bind(a.profile_report)
        pr = json.loads(a.profile_report.read_text())
        c['allocation_minutes'] = pr['recommended_full_minutes']
        c['work_cap_seconds'] = 60*c['allocation_minutes'] - 120
        c['profile_manifest'] = bind(pr['manifest_path'])
        c['profile_checkpoint'] = bind(Path(pr['manifest_path']).parent/'checkpoint.pt')
    audit(c)
    with a.output.open('x') as f:
        json.dump(c, f, indent=2)
    print('profile' if a.profile else 'full', c['updates'], len(c['training_ids']), c['allocation_minutes'])


if __name__ == '__main__':
    main()
