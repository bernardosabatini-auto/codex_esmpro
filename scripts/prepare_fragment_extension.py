"""Prepare only the two prospectively specified matched continuations."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from fragment_extension import audit_extension


def main():
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=['plain','weighted'],required=True);p.add_argument('--profile',type=Path);p.add_argument('--batch-four',action='store_true');p.add_argument('--second-block',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path);p.add_argument('--gate-data',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=a.protocol or root/('configs/fragment_extension_second_protocol.json' if a.second_block else 'configs/fragment_extension_batch4_protocol.json' if a.batch_four else 'configs/fragment_extension_protocol.json');spec=json.loads(protocol.read_text());parent=root/'runs'/spec['parents'][a.arm];report=root/'reports'/(parent.name+'.json');d=json.loads(report.read_text());c=d['config'].copy()
    if spec.get('sampling_control_mode'):c['sampling_control_mode']=spec['sampling_control_mode']
    for k in ('profile_report','profile_report_sha256','allocation_minutes','latent_weight_profile_audit'):c.pop(k,None)
    c.update(extension_arm=a.arm,profile_only=a.profile is None,seed=spec['seed'],updates=40 if a.profile is None else spec['updates'],evaluation_steps=[40] if a.profile is None else spec['evaluation_steps'],total_prior_updates=spec['total_prior_updates'],work_cap_seconds=480)
    for k,path in [('extension_protocol',protocol),('warm_protocol',protocol),('warm_parent_manifest',parent/'manifest.json'),('warm_parent_report',report),('warm_predictions',parent/'evaluation_2000.h5'),('checkpoint',parent/'ema_2000.ckpt')]:c[k]=str(path.resolve());c[k+'_sha256']=sha(path)
    if spec.get('training_protein_count')==512:
        for key in ('weight_breadth_protocol','weight_breadth_protocol_sha256','weight_breadth_baseline','weight_breadth_baseline_sha256'):c.pop(key,None)
        c['latent_weight_protocol']=str(protocol.resolve());c['latent_weight_protocol_sha256']=sha(protocol)
    if spec.get('data_protocol'):
        if a.gate_data is None:raise ValueError('Qualified target data required')
        run=a.gate_data.resolve()
        for key,path in [('extension_data_manifest',run/'manifest.json'),('extension_data_report',root/'reports'/(run.name+'.json')),('extension_data_targets',run/'targets.h5')]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text());estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240
        minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=60*minutes-90);print('Allocation minutes',minutes)
    audit_extension(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
