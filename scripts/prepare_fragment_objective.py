"""Gate decoded motif supervision on the completed distance-conditioner baseline."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads(a.baseline.read_text());c=d['config'].copy();protocol=root/'configs/fragment_objective_protocol.json';recipe=json.loads(protocol.read_text())
    if d['status']!='complete' or d['updates']!=2000 or c.get('distance_precision')!='fp64' or c.get('variant')!='geometry' or c.get('auxiliary_motif'):raise ValueError('Completed distance-only baseline required')
    scores={r['cohort']:r['arms']['conditioned'] for r in d['summaries'] if r['step']==2000}
    if scores['train']['joint_fraction']>=.5 and scores['development']['joint_fraction']>=.25:raise ValueError('Predeclared insufficient-retention condition not met')
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(auxiliary_motif=recipe['auxiliary'],profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780)
    for key,path in [('motif_objective_protocol',protocol),('motif_baseline_report',a.baseline)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['config']['motif_objective_protocol_sha256']!=c['motif_objective_protocol_sha256'] or pd['config']['motif_baseline_report_sha256']!=c['motif_baseline_report_sha256']:raise ValueError('Unqualified objective profile')
        estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Measured objective allocation minutes',minutes)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
