"""Match every non-target training draw and saved initialization across arms."""
import argparse
import json
import math
from pathlib import Path


def ready_command(root):
    for phase in ('profiles','full'):
        path=root/f'runs/repaint_student_training_{phase}.json';output=root/f'reports/repaint_student_training_{phase}_20261004'
        if not path.exists() or output.with_suffix('.json').exists():continue
        plan=json.loads(path.read_text());ids=plan['jobs']
        registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
        if len(ids)!=2 or len(set(ids))!=2 or any(i not in registry or registry[i]['completion_action']!='summarize_native_anchor_training' for i in ids):raise ValueError('Two registered student training jobs required')
        paths=[root/f'reports/native_anchor_training_{i}.json' for i in ids]
        if not all(p.exists() for p in paths):continue
        reports=[json.loads(p.read_text()) for p in paths]
        if any(r['status']!='complete' for r in reports):continue
        if any(r['protocol_sha256']!=plan['protocol_sha256'] or r['profile_only']!=(phase=='profiles') for r in reports):raise ValueError('Changed matched student phase')
        return [str(root/'scripts/compare_repaint_student_training.py'),'--runs',*[str(root/f'runs/native_anchor_training_{i}') for i in ids],'--output',str(output)]
    return None


def compare(runs,root):
    import h5py
    import numpy as np
    from repaint_student_training_core import audit,check_draws,INPUT_KEYS
    from teacher_coordinates_profile_core import sha
    rows={};sources=[]
    for run in runs:
        mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];audit(c)
        if (m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified']
                or d['manifest_sha256']!=sha(mp) or d['checkpoint_sha256']!=sha(run/f'ema_{c["updates"]}.ckpt')
                or c['arm'] in rows or m.get('saved_ema_reloaded') is not True):raise ValueError('Unqualified student training arm')
        rows[c['arm']]=(m,d,run);sources.extend(dict(path=str(p),sha256=sha(p)) for p in (mp,rp))
    if set(rows)!={'native_matched','repaint_positive'}:raise ValueError('Missing matched endpoint arm')
    a,b=[rows[k][0] for k in ('native_matched','repaint_positive')];ca,cb=a['config'],b['config']
    if any(ca[k]!=cb[k] for k in INPUT_KEYS+('sources','spec','training_ids','labels_manifest','updates','profile_only')):raise ValueError('Changed non-target training recipe')
    for key in ('generator_initial','adapter_initial','reference_initial','trainable_parameters','active_buckets'):
        if a[key]!=b[key]:raise ValueError('Changed model initialization')
    check_draws(a['training'],b['training'])
    if all(x['positive_sha256']==y['positive_sha256'] for x,y in zip(a['training'],b['training'])):raise ValueError('Target intervention did not execute')
    with h5py.File(rows['native_matched'][2]/'evaluation_0.h5') as x,h5py.File(rows['repaint_positive'][2]/'evaluation_0.h5') as y:
        for mode in ('conditioned','null'):
            for ident in ca['control_ids']:
                for key in ('latent','backbone'):
                    if not np.array_equal(x[mode+'/'+ident+'/'+key][:],y[mode+'/'+ident+'/'+key][:]):raise ValueError('Different initial predictions')
    minutes=math.ceil(max(1.8*(m['training_seconds']*ca['spec']['updates']/ca['updates']+m['elapsed_seconds']-m['training_seconds'])+120 for m,_,_ in rows.values())/60)
    prefix_controls=[]
    if not ca['profile_only']:
        profile=json.loads(Path(ca['profile_comparison']).read_text())
        for arm,(m,_,_) in rows.items():
            old=next(json.loads(Path(s['path']).read_text()) for s in profile['sources'] if Path(s['path']).name=='manifest.json' and json.loads(Path(s['path']).read_text())['config']['arm']==arm)
            if m['training'][:40]!=old['training']:raise ValueError('Profile/full40-step prefix differs')
            prefix_controls.append(arm)
    return dict(status='complete',qualified=True,profile_only=ca['profile_only'],matched_updates=ca['updates'],
                protocol_sha256=sha(ca['protocol']),labels_manifest_sha256=sha(ca['labels_manifest']),sources=sources,
                training_labels=13,training_families=9,initial_predictions_per_arm=32,recommended_full_minutes=max(10,minutes),
                profile_prefix_exact=prefix_controls,
                summary=[dict(arm=k,training_seconds=m['training_seconds'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB']) for k,(m,_,_) in rows.items()],
                scope='Numerical and resource qualification only. Both arms use identical isolated inputs and random draws; supervised endpoint latents differ. No designability or generalization claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=compare([p.resolve() for p in a.runs],Path(__file__).resolve().parents[1]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Matched isolated-input endpoint training\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='sources'},indent=2)+'\n```\n');print(json.dumps(d['summary']))


if __name__=='__main__':main()
