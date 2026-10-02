"""Bind direct fragment geometry to the established trainable-trunk recipe."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    baseline=root/'reports/fragment_training_49911511.json';design=root/'reports/trained_fragment_designability_49919660.json';d=json.loads(baseline.read_text());dd=json.loads(design.read_text());c=d['config'].copy()
    if d['status']!='complete' or d['updates']!=2000 or c['arm']!='adapter_only' or c.get('distance_precision')!='fp64' or c.get('auxiliary_motif') or dd['status']!='complete' or not dd['interpretation_qualified'] or dd['arm']!='geometry':raise ValueError('Invalid completed baselines')
    development=next(r for r in d['summaries'] if r['step']==2000 and r['cohort']=='development');refolds=next(r for r in dd['summaries'] if r['mode']=='conditioned')
    if development['arms']['conditioned']['joint_fraction'] or refolds['strict_joint_success']['count']:raise ValueError('Predeclared missing capacity prerequisite changed')
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(arm='full',profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780)
    for key,path in [('geometry_full_protocol',root/'configs/fragment_geometry_full_protocol.json'),('geometry_frozen_report',baseline),('geometry_designability_report',design)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['config']['arm']!='full' or pd['config']['geometry_full_protocol_sha256']!=c['geometry_full_protocol_sha256']:raise ValueError('Unqualified full-network profile')
        estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Measured full-network geometry allocation minutes',minutes)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
