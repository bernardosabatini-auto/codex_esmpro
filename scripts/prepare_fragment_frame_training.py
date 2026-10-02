"""Prepare a matched500-update conditional target-frame comparison."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from frame_target_audit import qualify_frame_data


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-report',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--confirmation',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads(a.data_report.read_text());dm=root/'runs'/a.data_report.stem/'manifest.json';m=json.loads(dm.read_text());c=json.loads((root/'reports/fragment_training_49937189.json').read_text())['config'].copy()
    if d['manifest_sha256']!=sha(dm) or m['config']['base_fragments_sha256']!=c['fragments_sha256']:raise ValueError('Invalid anchored target data')
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(target_frame_training=True,profile_only=a.profile is None,updates=40 if a.profile is None else 500,evaluation_steps=[40] if a.profile is None else [500],work_cap_seconds=780)
    for key,path in [('frame_data_report',a.data_report),('frame_data_manifest',dm),('fragments',dm.parent/'fragments.h5'),('target_frame_protocol',Path(m['config']['protocol']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.confirmation:
        cm=root/'runs'/a.confirmation.stem/'manifest.json';conf=json.loads(cm.read_text())
        for key,path in [('frame_confirmation_report',a.confirmation),('frame_confirmation_manifest',cm),('frame_confirmation_protocol',Path(conf['config']['protocol']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    c['frame_label_qualification']=qualify_frame_data(c)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['config']['fragments_sha256']!=c['fragments_sha256'] or not pd['config'].get('target_frame_training'):raise ValueError('Unqualified frame training profile')
        estimate=pd['training_seconds']/40*500+pd['evaluation_seconds']/2*12*2+240;minutes=math.ceil((estimate*1.2+120)/60);c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Frame pilot allocation minutes',minutes)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
