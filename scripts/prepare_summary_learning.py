"""Freeze the small matched summary feature training recipe, after cache/profile gates."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--features',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--profile-only',action='store_true');p.add_argument('--arm',choices=['projected_final','teacher_summary'],required=True);p.add_argument('--seed',type=int,default=2026100191);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/summary_learning_protocol.json';recipe=json.loads(protocol.read_text());features=json.loads(a.features.read_text())
    if features['status']!='complete' or not features['qualified'] or features['config']['protocol_sha256']!=sha(protocol):raise ValueError('features not qualified or protocol changed')
    if len(features['rows'])!=32 or len(features['controls'])!=4:raise ValueError('feature controls incomplete')
    if a.seed not in (recipe['first_seed'],recipe['replication_seed']):raise ValueError('undeclared seed')
    if a.profile_only and a.arm!=recipe['profile']['arm']:raise ValueError('profile the declared arm')
    if not a.profile_only:
        if a.profile is None:raise ValueError('profile required')
        profile=json.loads(a.profile.read_text())
        if profile['status']!='complete' or not profile['profile_only'] or profile['max_reserved_gib']>recipe['profile']['maximum_reserved_gib'] or profile['summary_adapter']['positive_gradient_updates']!=40 or profile['summary_adapter']['buckets']!=[128,256,384,512]:raise ValueError('learning profile failed')
    source=json.loads((root/'runs/overfit_49718446/manifest.json').read_text())['config']
    c={k:source[k] for k in ('label_manifest','label_manifest_sha256','protocol','protocol_sha256','arm','label_distribution','followup_protocol','followup_protocol_sha256')}
    c.update(summary_arm=a.arm,summary_protocol=str(protocol),summary_protocol_sha256=sha(protocol),feature_manifest=str(a.features.resolve()),feature_manifest_sha256=sha(a.features),seed=a.seed,evaluation_seed=recipe['evaluation_seed'],learning_rate=recipe['flow_learning_rate'],ema_decay=recipe['ema_decay'],warmup_updates=recipe['warmup_updates'],batches=recipe['batches'],profile_only=a.profile_only,updates=40 if a.profile_only else 500,evaluation_steps=[40] if a.profile_only else [500],evaluation_guidance=[1],decoder_steps=3,maximum_profile_gib=80,work_cap_seconds=780 if a.profile_only else 3300)
    if not a.profile_only:c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile))
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
