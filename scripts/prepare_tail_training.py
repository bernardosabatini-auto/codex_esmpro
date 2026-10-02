"""Bind tail-only adaptation to the matched full-network corpus and short profile."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from expanded_corpus import metadata


def prepare(root,profile=None):
    protocol=root/'configs/tail122_protocol.json';recipe=json.loads(protocol.read_text())
    c=json.loads((root/'runs/expanded_profile.json').read_text())
    metadata(c)
    c.update(trainable_tail_blocks=recipe['trainable_tail_blocks'])
    for name in ('protocol','followup_protocol'):
        c[name]=str(protocol.resolve());c[name+'_sha256']=sha(protocol)
    if profile is not None:
        report=json.loads(profile.read_text());run=root/'runs'/profile.stem
        m=json.loads((run/'manifest.json').read_text());device=json.loads((run/'device_metadata.json').read_text())
        subset=m.get('training_subset',{})
        if (report['status']!='complete' or not report['profile_only'] or report['max_reserved_gib']>80
            or m['status']!='complete' or m['updates']!=40 or m['config']!=c
            or not subset.get('frozen_unchanged') or subset.get('tail_blocks')!=4
            or not 0<subset.get('trainable_parameters',0)<subset.get('total_parameters',0)
            or 'RTX PRO 6000 Blackwell' not in device['cuda_device_name']):raise ValueError('tail profile failed or mismatched')
        if not m['training'] or any(not 0<r['gradient_norm']<float('inf') or not 0<=r['flow_loss']<float('inf') for r in m['training']):raise ValueError('invalid gradients/loss')
        c.update(profile_only=False,updates=recipe['updates'],evaluation_steps=recipe['evaluation_steps'],work_cap_seconds=6840,profile_report=str(profile.resolve()),profile_report_sha256=sha(profile))
        return [dict(c,seed=seed) for seed in recipe['seeds']]
    return [c]


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    configs=prepare(Path(__file__).resolve().parents[1],a.profile)
    for c in configs:
        output=a.output.with_name(f'{a.output.stem}_{c["seed"]}.json') if a.profile else a.output
        output.write_text(json.dumps(c,indent=2)+'\n');print(output)

if __name__=='__main__':main()
