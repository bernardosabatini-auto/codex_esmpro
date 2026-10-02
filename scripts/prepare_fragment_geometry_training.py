"""Evidence-gated direct-geometry conditioner, preserving the matched baseline."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline-reports',type=Path,nargs=2,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();reports=[json.loads(p.read_text()) for p in a.baseline_reports];root=Path(__file__).resolve().parents[1]
    if [d['config']['arm'] for d in reports]!=['adapter_only','full'] or any(d['status']!='complete' or d['updates']!=2000 or d['capacity_gate_passed'] for d in reports):raise ValueError('Predeclared failed-capacity prerequisite not met')
    c=reports[0]['config'].copy();c.pop('profile_report',None);c.pop('profile_report_sha256',None);c.pop('allocation_minutes',None);c.update(variant='geometry',profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780,baseline_reports=[dict(path=str(p.resolve()),sha256=sha(p)) for p in a.baseline_reports]);protocol=root/'configs/fragment_geometry_protocol.json';c.update(geometry_protocol=str(protocol.resolve()),geometry_protocol_sha256=sha(protocol))
    if a.profile:
        d=json.loads(a.profile.read_text())
        if not d['profile_qualified'] or d['config']['geometry_protocol_sha256']!=c['geometry_protocol_sha256'] or d['config']['data_manifest_sha256']!=c['data_manifest_sha256']:raise ValueError('Invalid geometry profile')
        estimate=d['training_seconds']/40*2000+d['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Measured full allocation minutes',minutes)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
