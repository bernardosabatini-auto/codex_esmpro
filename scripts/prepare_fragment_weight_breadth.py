"""Prepare the fixed weighted512 profile or its qualified training run."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from fragment_weight_breadth import audit


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_weight_breadth_protocol.json';spec=json.loads(protocol.read_text());base=root/'runs'/spec['baseline']/'manifest.json'
    c=json.loads(base.read_text())['config'].copy()
    report=root/'reports'/(spec['baseline']+'.json');d=json.loads(report.read_text())
    if d['status']!='complete' or d['manifest_sha256']!=sha(base):raise ValueError('Unaudited baseline')
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780,latent_motif_weight=3.)
    for key,path in [('weight_breadth_protocol',protocol),('weight_breadth_baseline',base),('latent_weight_protocol',protocol)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if a.profile:
        from audit_backbone_token_profile import audit_matched_profile
        pd=json.loads(a.profile.read_text());audit(pd['config'])
        if pd['config']['weight_breadth_protocol_sha256']!=c['weight_breadth_protocol_sha256']:raise ValueError('Different profile protocol')
        c['latent_weight_profile_audit']=audit_matched_profile(root,a.profile,spec['baseline_profile'].rsplit('_',1)[1])
        estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60))
        c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90)
        print('Allocation minutes',minutes)
    audit(c);a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
