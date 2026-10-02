"""Gate a fresh-optimizer continuation on an improving completed parent."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--data-report',type=Path);p.add_argument('--rollout',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];parent=root/'runs/fragment_training_49929751';report=root/'reports/fragment_training_49929751.json';d=json.loads(report.read_text());c=d['config'].copy();protocol=root/'configs/fragment_continuation_protocol.json'
    if d['status']!='complete' or d['updates']!=2000 or c['arm']!='full' or c.get('variant')!='geometry' or c.get('auxiliary_motif') or d['manifest_sha256']!=sha(parent/'manifest.json'):raise ValueError('Unqualified parent')
    rows={(r['step'],r['cohort']):r['arms']['conditioned'] for r in d['summaries']};train=rows[2000,'train'];dev=rows[2000,'development']
    if train['mean_motif_drms']>.8*rows[500,'train']['mean_motif_drms'] or dev['raw_valid_fraction']<.95 or train['joint_fraction']>=.5 or dev['joint_fraction']>=.25:raise ValueError('Continuation prerequisite not met')
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    c.update(warm_start=True,seed=json.loads(protocol.read_text())['seed'],profile_only=a.profile is None,updates=40 if a.profile is None else 2000,evaluation_steps=[40] if a.profile is None else [500,2000],work_cap_seconds=780,total_prior_updates=2000)
    for key,path in [('checkpoint',parent/'ema_2000.ckpt'),('warm_protocol',protocol),('warm_parent_manifest',parent/'manifest.json'),('warm_parent_report',report),('warm_predictions',parent/'evaluation_2000.h5')]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.rollout:
        if a.data_report:raise ValueError('Rollout changes objective only, not data')
        path=root/'configs/fragment_rollout_protocol.json';c.update(rollout_protocol=str(path.resolve()),rollout_protocol_sha256=sha(path),rollout_motif=json.loads(path.read_text())['auxiliary'])
    if a.data_report:
        dd=json.loads(a.data_report.read_text());dm_path=root/'runs'/a.data_report.stem/'manifest.json';dm=json.loads(dm_path.read_text());dc=dm['config']
        if dd['status']!='complete' or not dd['training_gate_passed'] or dd['training_proteins']!=128 or dd['manifest_sha256']!=sha(dm_path) or not dc.get('expanded_fragment_data') or dc['base_fragments_sha256']!=c['fragments_sha256']:raise ValueError('Unqualified expanded fragment corpus')
        c.update(expanded_fragment_data=True,evaluation_train_ids=dc['base_training_ids'])
        for key,path in [('data_report',a.data_report),('data_manifest',dm_path),('fragments',dm_path.parent/'fragments.h5'),('expanded_protocol',Path(dc['expanded_protocol']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['config']['warm_protocol_sha256']!=c['warm_protocol_sha256'] or pd['config']['checkpoint_sha256']!=c['checkpoint_sha256'] or pd['config']['fragments_sha256']!=c['fragments_sha256']:raise ValueError('Unqualified continuation profile')
        if pd['config'].get('rollout_motif')!=c.get('rollout_motif') or pd['config'].get('rollout_protocol_sha256')!=c.get('rollout_protocol_sha256'):raise ValueError('Mismatched rollout profile')
        estimate=pd['training_seconds']/40*2000+pd['evaluation_seconds']/2*12*3+240;minutes=max(15,math.ceil((estimate*1.2+120)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Continuation allocation minutes',minutes)
    if a.rollout and a.profile and c['allocation_minutes']>150:raise ValueError('Rollout cost exceeds declared150minute cap')
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
