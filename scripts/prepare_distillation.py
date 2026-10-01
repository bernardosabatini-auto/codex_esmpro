"""Freeze completed teacher shards into a matched training configuration."""
import argparse,hashlib,json
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--shards',type=Path,nargs='+',required=True);p.add_argument('--profile-only',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--profile-result',type=Path);p.add_argument('--audit-only',action='store_true');p.add_argument('--audit-result',type=Path);a=p.parse_args()
    protocol=json.loads(Path('configs/distillation_protocol.json').read_text());base=json.loads(Path('runs/conditioning_config.json').read_text());shards=[];covered=set()
    for run in a.shards:
        path=run/'manifest.json';m=json.loads(path.read_text())
        if m['status']!='complete' or len(m['records'])!=128 or m['config']['latent_frame']!='first_residue_N_CA_C' or m['config']['selection_sha256']!=base['selection_sha256']:raise ValueError('incomplete or mismatched label shard')
        ids={r['id'] for r in m['records']}
        if len(ids)!=128 or covered&ids:raise ValueError('duplicate label targets')
        covered|=ids;shards.append(dict(manifest=str(path.resolve()),manifest_sha256=sha(path),labels_sha256=sha(run/'labels.h5')))
    if len(covered)!=(128 if a.profile_only else 512):raise ValueError('wrong number of training labels')
    batches={'128':32,'256':16,'384':8,'512':8}
    config=dict(selection=base['selection'],selection_sha256=base['selection_sha256'],embedding_cache=base['embedding_cache'],label_shards=shards,seed=2026100131,evaluation_seed=base['evaluation_seed'],batches=batches,learning_rate=protocol['optimizer']['learning_rate'],ema_decay=protocol['optimizer']['ema_decay'],warmup_updates=protocol['warmup_updates'],updates=64 if a.profile_only else protocol['updates'],evaluation_steps=[64] if a.profile_only else protocol['evaluate_at_updates'][1:],work_cap_seconds=780 if a.profile_only else 5700,profile_only=a.profile_only,protocol_sha256=sha('configs/distillation_protocol.json'))
    if a.audit_only:
        if a.profile_only:raise ValueError('audit requires full corpus')
        config['work_cap_seconds']=780;a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(config,indent=2)+'\n');return
    if not a.profile_only:
        if a.audit_result is None:raise ValueError('full-corpus reconstruction audit required')
        audit=json.loads(a.audit_result.read_text())
        if audit['status']!='complete' or not audit['training_gate_passed'] or audit['label_shards']!=shards:raise ValueError('label reconstruction audit gate closed')
        config.update(audit_result=str(a.audit_result.resolve()),audit_result_sha256=sha(a.audit_result))
        if a.profile_result is None:raise ValueError('successful capacity profile required')
        result=json.loads(a.profile_result.read_text())
        if result['status']!='complete' or not result['profile_only'] or result['max_reserved_gib']>110:raise ValueError('capacity profile gate failed')
        config.update(profile_result=str(a.profile_result.resolve()),profile_result_sha256=sha(a.profile_result))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.profile_only:
        config['arm']='balanced';a.output.write_text(json.dumps(config,indent=2)+'\n')
    else:
        for arm in protocol['arms']:
            config['arm']=arm;a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':main()
