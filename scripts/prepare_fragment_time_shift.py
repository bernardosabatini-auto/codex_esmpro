"""Prepare the fixed high-noise conditional-training profile or qualified run."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from fragment_time_shift import audit_config,compare


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_time_shift_protocol.json';spec=json.loads(protocol.read_text());base=root/'runs'/spec['baseline']/'manifest.json';d=json.loads((root/'reports'/(spec['baseline']+'.json')).read_text())
    if d['status']!='complete' or d['manifest_sha256']!=sha(base):raise ValueError('Unaudited baseline')
    c=d['config'].copy()
    for key in ('profile_report','profile_report_sha256','allocation_minutes','latent_weight_profile_audit'):c.pop(key,None)
    c.update(profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780,conditional_time_shift=-1.)
    for key,path in [('time_protocol',protocol),('time_baseline_manifest',base)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text());candidate=root/'runs'/a.profile.stem
        if not pd['profile_qualified'] or pd['manifest_sha256']!=sha(candidate/'manifest.json'):raise ValueError('Unqualified time profile')
        c['time_profile_audit']=compare(root,candidate);estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60))
        c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Allocation minutes',minutes)
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
