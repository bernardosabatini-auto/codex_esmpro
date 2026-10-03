"""Matched initialization and draw audit; never selects quality checkpoints."""
import argparse
import json
import math
from pathlib import Path


def ready_command(root):
    for phase,profile_only in [('profiles',True),('full',False)]:
        path=root/'runs'/('native_anchor_training_'+phase+'.json')
        if not path.exists():continue
        plan=json.loads(path.read_text());ids=plan['jobs']
        if len(ids)!=2 or len(set(ids))!=2:raise ValueError('Expected two declared native training arms')
        registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
        if any(i not in registry or registry[i].get('completion_action')!='summarize_native_anchor_training' for i in ids):raise ValueError('Unregistered native training comparison')
        reports=[root/f'reports/native_anchor_training_{i}.json' for i in ids]
        if not all(p.exists() for p in reports):continue
        rows=[json.loads(p.read_text()) for p in reports]
        if any(r['status']!='complete' for r in rows):continue
        if any(r['protocol_sha256']!=plan['protocol_sha256'] or r['profile_only']!=profile_only for r in rows):raise ValueError('Changed matched training phase')
        output=root/'reports'/('native_anchor_training_'+phase+'_20261003')
        if output.with_suffix('.json').exists():continue
        return [str(root/'scripts/compare_native_anchor_training.py'),'--runs',*[str(root/f'runs/native_anchor_training_{i}') for i in ids],'--output',str(output)]
    return None


def check_draws(a,b):
    fields=('step','length','batch','ids','learning_rate_factor','positive_sha256','negative_sha256','noise_sha256','time_sha256','rng_sha256','self_conditioned')
    if len(a)!=len(b) or any(x[k]!=y[k] for x,y in zip(a,b) for k in fields):raise ValueError('Unmatched training draws')


def compare(runs,root):
    import h5py
    import numpy as np
    from prepare_overfit import sha
    rows={};sources=[]
    for run in runs:
        run=run.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config']
        if m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified'] or d['manifest_sha256']!=sha(mp) or d['checkpoint_sha256']!=sha(run/f'ema_{c["updates"]}.ckpt') or c['arm'] in rows:raise ValueError('Unqualified matched training arm')
        rows[c['arm']]=(m,d,run);sources.append(dict(manifest=str(mp),manifest_sha256=sha(mp),report=str(rp),report_sha256=sha(rp)))
    if set(rows)!={'positive','contrastive'}:raise ValueError('Missing comparison arm')
    a,b=[rows[k][0] for k in ('positive','contrastive')];ca,cb=a['config'],b['config']
    for key in ('spec','sources','training_ids','control_ids','checkpoint','decoder_checkpoint','fragments','initial_predictions','sampling_seed','updates','profile_only'):
        if ca[key]!=cb[key]:raise ValueError('Changed paired configuration: '+key)
    for key in ('generator_initial','adapter_initial','reference_initial','trainable_parameters','active_buckets'):
        if a[key]!=b[key]:raise ValueError('Changed paired initialization')
    check_draws(a['training'],b['training'])
    with h5py.File(rows['positive'][2]/'evaluation_0.h5') as x,h5py.File(rows['contrastive'][2]/'evaluation_0.h5') as y:
        for mode in ('conditioned','null'):
            for ident in ca['control_ids']:
                if not np.array_equal(x[mode+'/'+ident+'/latent'][:],y[mode+'/'+ident+'/latent'][:]):raise ValueError('Different initial predictions')
    minutes=math.ceil(max(1.8*(m['training_seconds']*ca['spec']['updates']/ca['updates']+m['elapsed_seconds']-m['training_seconds'])+120 for m,_,_ in rows.values())/60)
    return dict(status='complete',qualified=True,profile_only=ca['profile_only'],protocol_sha256=sha(ca['protocol']),matched_updates=ca['updates'],initial_predictions_per_arm=32,training_pairs=len(ca['training_ids']),
                sources=sources,recommended_full_minutes=max(10,minutes),summary=[dict(arm=k,training_seconds=m['training_seconds'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB']) for k,(m,_,_) in rows.items()],
                scope='Paired numerical and resource qualification, not designability or performance evidence.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=compare(a.runs,Path(__file__).resolve().parents[1])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Matched native-anchor training\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='sources'},indent=2)+'\n```\n');print(json.dumps({k:v for k,v in d.items() if k!='sources'}))


if __name__=='__main__':main()
