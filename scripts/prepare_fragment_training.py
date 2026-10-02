"""Bind fragment training to audited input data and a measured resource profile."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-report',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads(a.data_report.read_text())
    if d['status']!='complete' or not d['training_gate_passed']:raise ValueError('Data gate failed')
    jid=a.data_report.stem.removeprefix('fragment_data_');manifest=root/'runs'/('fragment_data_'+jid)/'manifest.json';m=json.loads(manifest.read_text());protocol=root/'configs/fragment_conditioning_protocol.json';r=json.loads(protocol.read_text());initial=root/'runs/generative_pilot_49855378/manifest.json';im=json.loads(initial.read_text())
    if sha(manifest)!=d['manifest_sha256'] or im['status']!='complete':raise ValueError('Changed/incomplete sources')
    c=dict(seed=r['seed'],batches=r['batches'],profile_only=a.profile is None,arm='full',updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780,control_ids=im['config']['control_ids'])
    for key,path in [('protocol',protocol),('data_report',a.data_report),('data_manifest',manifest),('fragments',manifest.parent/'fragments.h5'),('checkpoint',root/'runs/inference_checkpoints/original459m_ema.ckpt'),('decoder_checkpoint',Path(m['config']['decoder_checkpoint'])),('initial_manifest',initial),('initial_predictions',initial.parent/'predictions.h5')]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if c['fragments_sha256']!=d['fragments_sha256']:raise ValueError('Changed fragments')
    if a.profile is None:a.output.write_text(json.dumps(c,indent=2)+'\n');print('Prepared40update profile,15minute allocation')
    else:
        profile=json.loads(a.profile.read_text())
        if not profile['profile_qualified'] or profile['config']['data_manifest_sha256']!=c['data_manifest_sha256'] or profile['config']['protocol_sha256']!=c['protocol_sha256']:raise ValueError('Unqualified/mismatched profile')
        estimate=profile['training_seconds']/40*2000+profile['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(work_cap_seconds=minutes*60-90,profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes)
        for arm in r['arms']:c['arm']=arm;a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(c,indent=2)+'\n')
        print('Prepared both2000update arms; allocation minutes',minutes)

if __name__=='__main__':main()
