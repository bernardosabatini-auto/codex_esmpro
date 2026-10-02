"""Bind the data-breadth experiment to a complete corpus and measured RTX profile."""
import argparse,json
from pathlib import Path
from expansion_corpus import metadata,load
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/expanded_labels_training_protocol.json';recipe=json.loads(protocol.read_text());inv=json.loads(a.inventory.read_text())
    c={key:recipe[key] for key in ('updates','evaluation_steps','evaluation_guidance','evaluation_seed','learning_rate','ema_decay','warmup_updates','batches')}
    c.update(corpus_kind='expansion',arm='aligned_teacher',label_distribution='balanced',decoder_steps=3,seed=recipe['seeds'][0],profile_only=True,updates=40,evaluation_steps=[40],work_cap_seconds=480,maximum_profile_gib=80,evaluation_ids=inv['evaluation_ids'])
    for key,path in dict(corpus_inventory=a.inventory.resolve(),protocol=protocol,followup_protocol=protocol).items():c[key]=str(path);c[key+'_sha256']=sha(path)
    c['checkpoint_sha256']=json.loads((root/'runs/overfit_native_49736749/manifest.json').read_text())['config']['checkpoint_sha256']
    metadata(c);records,buckets=load(c);print(json.dumps(dict(targets=len(records),buckets={k:len(v) for k,v in buckets.items()},evaluation_targets=len(c['evaluation_ids']))),flush=True)
    if a.profile:
        prof=json.loads(a.profile.read_text());run=root/'runs'/a.profile.stem;pm=json.loads((run/'manifest.json').read_text());device=json.loads((run/'device_metadata.json').read_text())
        if prof['status']!='complete' or not prof['profile_only'] or prof['max_reserved_gib']>80 or pm['status']!='complete' or pm['updates']!=40 or pm['config']!=c or 'RTX PRO 6000 Blackwell' not in device['cuda_device_name']:raise ValueError('wrong or failed RTX capacity profile')
        c.update(profile_only=False,updates=recipe['updates'],evaluation_steps=recipe['evaluation_steps'],work_cap_seconds=8640,profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile))
        for seed in recipe['seeds']:
            path=a.output.with_name(f'{a.output.stem}_{seed}.json');path.write_text(json.dumps(dict(c,seed=seed),indent=2)+'\n');print(path)
    else:a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
