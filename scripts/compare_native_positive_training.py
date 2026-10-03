"""Audit expanded positives against the completed ten-positive control."""
import argparse
import json
import math
from pathlib import Path


def ready_command(root):
    for phase in ('profiles','full'):
        path=root/f'runs/native_positive_training_{phase}.json';output=root/f'reports/native_positive_training_{phase}_20261003'
        if not path.exists() or output.with_suffix('.json').exists():continue
        plan=json.loads(path.read_text());jid=plan['job'];registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
        if jid not in registry or registry[jid]['completion_action']!='summarize_native_anchor_training':raise ValueError('Unregistered positive coverage training')
        report=root/f'reports/native_anchor_training_{jid}.json'
        if not report.exists():continue
        d=json.loads(report.read_text())
        if d['status']!='complete':continue
        if d['protocol_sha256']!=plan['protocol_sha256'] or d['profile_only']!=(phase=='profiles'):raise ValueError('Changed positive training phase')
        return [str(root/'scripts/compare_native_positive_training.py'),'--run',str(root/f'runs/native_anchor_training_{jid}'),'--output',str(output)]
    return None


def compare(run,root):
    import h5py
    import numpy as np
    from native_positive_training_core import audit,check_draws,NUMERIC_KEYS,INPUT_KEYS
    from prepare_overfit import sha
    mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];spec,labels=audit(c)
    old=root/('runs/native_anchor_training_50206089' if c['profile_only'] else 'runs/native_anchor_training_50209404')
    op=old/'manifest.json';orr=root/'reports'/(old.name+'.json');om=json.loads(op.read_text());od=json.loads(orr.read_text());oc=om['config']
    for model,report,manifest,directory in [(m,d,mp,run),(om,od,op,old)]:
        if (model['status']!='complete' or report['status']!='complete' or not report['numerically_qualified']
                or report['manifest_sha256']!=sha(manifest) or report['checkpoint_sha256']!=sha(directory/f'ema_{model["config"]["updates"]}.ckpt')):raise ValueError('Unqualified training audit')
    if any(spec[k]!=oc['spec'][k] for k in NUMERIC_KEYS) or any(c[k]!=oc[k] for k in INPUT_KEYS+('updates','profile_only')):raise ValueError('Changed matched recipe/input')
    for key in ('generator_initial','adapter_initial','reference_initial','trainable_parameters','active_buckets'):
        if m[key]!=om[key]:raise ValueError('Changed initialization: '+key)
    check_draws(m['training'],om['training'])
    with h5py.File(run/'evaluation_0.h5') as x,h5py.File(old/'evaluation_0.h5') as y:
        for mode in ('conditioned','null'):
            for ident in c['control_ids']:
                if not np.array_equal(x[mode+'/'+ident+'/latent'][:],y[mode+'/'+ident+'/latent'][:]):raise ValueError('Different initial predictions')
    minutes=math.ceil((1.8*(m['training_seconds']*spec['updates']/c['updates']+m['elapsed_seconds']-m['training_seconds'])+120)/60)
    return dict(status='complete',qualified=True,profile_only=c['profile_only'],protocol_sha256=sha(c['protocol']),labels_manifest_sha256=sha(c['labels_manifest']),matched_updates=c['updates'],
                training_positives=len(c['training_ids']),control_positives=len(oc['training_ids']),initial_predictions_per_arm=32,
                sources=[dict(path=str(p),sha256=sha(p)) for p in (mp,rp,op,orr)],recommended_full_minutes=max(10,minutes),
                training_seconds=m['training_seconds'],control_training_seconds=om['training_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],
                scope='Identical numeric recipe, initialization, historical controls and noise/time/history draws. Protein draws/endpoints intentionally differ to test verified-positive coverage. No quality or generalization claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=compare(a.run.resolve(),Path(__file__).resolve().parents[1])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Positive coverage training audit\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='sources'},indent=2)+'\n```\n');print(json.dumps({k:v for k,v in d.items() if k!='sources'}))


if __name__=='__main__':main()
