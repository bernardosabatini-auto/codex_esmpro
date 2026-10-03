import argparse
import json
from pathlib import Path
from native_anchor_training_core import audit,load_pairs
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=['positive','contrastive'],required=True);p.add_argument('--profile',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--profile-comparison',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/native_anchor_training_protocol.json';spec=json.loads(protocol.read_text())
    lp=root/'runs/native_anchor_labels_20261003/manifest.json';labels=json.loads(lp.read_text());gm=json.loads(Path(labels['generation_manifest']).read_text())
    c=dict(arm=a.arm,spec=spec,profile_only=a.profile,updates=spec['profile_updates'] if a.profile else spec['updates'],sources=[],
           training_ids=sorted(r['target_id'] for r in labels['rows']),control_ids=labels['control_ids'],sampling_seed=gm['config']['spec']['seed'],
           allocation_minutes=20 if a.profile else 30,work_cap_seconds=1080 if a.profile else 1680)
    def bind(path):
        path=Path(path).resolve();c['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    for key,path in [('protocol',protocol),('labels_manifest',lp),('checkpoint',labels['checkpoint']),('decoder_checkpoint',labels['decoder_checkpoint']),('fragments',labels['fragments']),('initial_predictions',Path(labels['generation_manifest']).parent/'predictions.h5')]:c[key]=bind(path)
    if not a.profile:
        if a.profile_comparison is None:raise ValueError('Full training requires a qualified paired profile')
        c['profile_comparison']=bind(a.profile_comparison)
        profile=json.loads(a.profile_comparison.read_text());c['allocation_minutes']=profile['recommended_full_minutes'];c['work_cap_seconds']=60*c['allocation_minutes']-120
    load_pairs(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print(a.arm,c['updates'],len(c['training_ids']))


if __name__=='__main__':main()
