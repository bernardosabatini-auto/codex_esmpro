"""Bind the broader matched-prior experiment to certified existing arrays."""
import argparse,hashlib,json
from pathlib import Path
import h5py
from expanded_corpus import metadata,load
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/reliable122_protocol.json';recipe=json.loads(protocol.read_text())
    transfer=root/'reports/overfit_native_49736749.json';t=json.loads(transfer.read_text())
    capacity=root/'reports/overfit_balanced_comparison_500.json';g=json.loads(capacity.read_text())
    if t['status']!='complete' or not t['summaries']['aligned_teacher_balanced_cfg1']['quality_passed'] or not g['matched'] or not g['capacity_checks']['aligned_teacher']['passed']:raise ValueError('capacity/transfer prerequisite failed')
    c={key:recipe[key] for key in ('updates','evaluation_steps','evaluation_guidance','evaluation_seed','learning_rate','ema_decay','warmup_updates','batches')}
    for name,path in dict(corpus_inventory=root/'runs/reliable122_inventory.json',reconstruction_certificate=root/'reports/reliable122_reconstruction_bounds.json',protocol=protocol,followup_protocol=protocol,transfer_prerequisite=transfer,capacity_prerequisite=capacity).items():c[name]=str(path);c[name+'_sha256']=sha(path)
    c.update(arm='aligned_teacher',label_distribution='balanced',decoder_steps=3,seed=recipe['seeds'][0],profile_only=True,updates=40,evaluation_steps=[40],work_cap_seconds=480,maximum_profile_gib=80)
    c['checkpoint_sha256']=json.loads((root/'runs/overfit_native_49736749/manifest.json').read_text())['config']['checkpoint_sha256']
    inventory=metadata(c);c['embedding_arrays_sha256']={}
    with h5py.File(inventory['embedding_cache']) as cache:
        for row in inventory['targets']:c['embedding_arrays_sha256'][row['id']]=hashlib.sha256(cache['train'][row['id']]['80'][:].tobytes()).hexdigest()
    records,buckets=load(c)
    print(json.dumps(dict(loaded=len(records),buckets={k:len(v) for k,v in buckets.items()})),flush=True)
    if a.profile:
        prof=json.loads(a.profile.read_text())
        if prof['status']!='complete' or not prof['profile_only'] or prof['max_reserved_gib']>80:raise ValueError('RTX capacity profile failed')
        profile_run=root/'runs'/a.profile.stem
        pm=json.loads((profile_run/'manifest.json').read_text());device=json.loads((profile_run/'device_metadata.json').read_text())
        if pm['status']!='complete' or pm['updates']!=40 or pm['config']!=c or 'RTX PRO 6000 Blackwell' not in device['cuda_device_name']:raise ValueError('wrong corpus/configuration or hardware in capacity profile')
        c.update(profile_only=False,updates=recipe['updates'],evaluation_steps=recipe['evaluation_steps'],work_cap_seconds=8640,profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile))
        for seed in recipe['seeds']:
            for prior in recipe['arms']:
                config=dict(c,seed=seed,label_distribution=prior)
                a.output.with_name(f'{a.output.stem}_{prior}_{seed}.json').write_text(json.dumps(config,indent=2)+'\n')
    else:a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
