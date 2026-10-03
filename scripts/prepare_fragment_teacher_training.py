"""Clone the current weighted duration control, changing only endpoint targets."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from fragment_teacher_augmentation_training import audit_config


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline-config',type=Path);p.add_argument('--baseline-profile',type=Path);p.add_argument('--baseline-run',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];baseline=(a.baseline_config or root/'runs/fragment_extension_second_weighted_training.json').resolve();c=json.loads(baseline.read_text());baseline_profile=(a.baseline_profile or root/'runs/fragment_training_50081275/manifest.json').resolve()
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=480)
    data=a.data.resolve();data_manifest=json.loads((data/'manifest.json').read_text())
    if a.baseline_run:c['augmentation_baseline_run']=str(a.baseline_run.resolve())
    for key,path in [('augmentation_protocol',Path(data_manifest['config']['protocol'])),('augmentation_manifest',data/'manifest.json'),('augmentation_report',root/'reports'/(data.name+'.json')),('augmentation_targets',data/'targets.h5'),('augmentation_baseline_config',baseline),('augmentation_baseline_profile',baseline_profile)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if a.profile:
        d=json.loads(a.profile.read_text());estimate=d['training_seconds']/40*2000+d['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Allocation minutes',minutes)
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
