import argparse
import json
from pathlib import Path
from prepare_overfit import sha
from train_fragment_context_flow import load_data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--profile-report', type=Path)
    a = p.parse_args(); path = a.data.resolve()/'manifest.json'; data = json.loads(path.read_text())
    for source in data['sources']:
        if sha(source['path']) != source['sha256']:
            raise ValueError('Changed original data/protocol/panel')
    profile = a.profile_report is None
    c = dict(data_manifest=str(path), data_manifest_sha256=sha(path), profile_only=profile,
             updates=data['spec']['profile_updates' if profile else 'updates'],
             allocation_minutes=10, work_cap_seconds=480)
    if not profile:
        report = json.loads(a.profile_report.read_text())
        if (report['status'] != 'complete' or not report['qualified'] or not report['profile_only']
                or report['data_manifest_sha256'] != c['data_manifest_sha256']):
            raise ValueError('Matching qualified profile required')
        c.update(profile_report=str(a.profile_report.resolve()), profile_report_sha256=sha(a.profile_report),
                 allocation_minutes=report['recommended_full_minutes'],
                 work_cap_seconds=report['recommended_full_minutes']*60-120)
    load_data(c)
    with a.output.open('x') as f:
        json.dump(c, f, indent=2)
    print(json.dumps(c))


if __name__ == '__main__': main()
