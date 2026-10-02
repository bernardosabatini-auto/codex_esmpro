"""Choose a bounded horizon from the completed actual-rollout cost profile."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads(a.profile.read_text());c=d['config'].copy();run=root/'runs'/a.profile.stem;m=json.loads((run/'manifest.json').read_text());baseline=Path(c.get('rollout_control_manifest',root/'runs/fragment_training_49939857/manifest.json'));b=json.loads(baseline.read_text())
    if not d['profile_qualified'] or d['manifest_sha256']!=sha(run/'manifest.json') or not c.get('rollout_motif') or (c.get('expanded_fragment_data') and not c.get('rollout_breadth_protocol')) or c['updates']!=40:raise ValueError('Unqualified actual-rollout profile')
    keys=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    if len(m['training'])!=40 or any(any(x[k]!=y[k] for k in keys) for x,y in zip(b['training'][:40],m['training'])) or b['adapter_initial']!=m['adapter_initial']:raise ValueError('Unmatched profile draws')
    full_estimate=d['training_seconds']/40*2000+d['evaluation_seconds']/2*12*3+240
    if math.ceil((full_estimate*1.2+120)/60)<=150:raise ValueError('Original full recipe is affordable; shorter cost stage not justified')
    estimate=d['training_seconds']/40*500+d['evaluation_seconds']/2*12*2+240;minutes=math.ceil((estimate*1.2+120)/60)
    if minutes>90:raise ValueError('Pilot exceeds90minute allocation')
    c.update(rollout_pilot=True,profile_only=False,updates=500,evaluation_steps=[500],allocation_minutes=minutes,work_cap_seconds=minutes*60-90)
    for key,path in [('rollout_pilot_protocol',root/'configs/fragment_rollout_pilot_protocol.json'),('profile_report',a.profile),('rollout_control_manifest',baseline)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Pilot allocation minutes',minutes)

if __name__=='__main__':main()
