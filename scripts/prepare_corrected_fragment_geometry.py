"""Numerical correction restart, gated by the frozen failed-checkpoint diagnostic."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--diagnostic',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads(a.diagnostic.read_text())
    if d['status']!='complete' or not d['corrected_precision_profile_qualified']:raise ValueError('Precision correction not qualified')
    parent=root/'runs/fragment_training_49904816/manifest.json';m=json.loads(parent.read_text())
    if m['status']!='failed' or m['updates']!=500:raise ValueError('Unexpected source run')
    diagnostic_manifest=root/'runs'/a.diagnostic.stem/'manifest.json';dm=json.loads(diagnostic_manifest.read_text())
    if sha(diagnostic_manifest)!=d['manifest_sha256'] or dm['config']['parent_manifest_sha256']!=sha(parent):raise ValueError('Diagnostic provenance changed')
    c=m['config'].copy()
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(distance_precision='fp64',profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780)
    for key,path in [('geometry_precision_protocol',root/'configs/fragment_geometry_precision_protocol.json'),('pose_diagnostic_report',a.diagnostic)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['config']['distance_precision']!='fp64' or pd['config']['geometry_precision_protocol_sha256']!=c['geometry_precision_protocol_sha256']:raise ValueError('Corrected resource profile not qualified')
        estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Corrected full allocation minutes',minutes)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
