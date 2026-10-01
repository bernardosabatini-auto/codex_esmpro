"""Bind audited aligned labels to the unchanged matched training recipe."""
import argparse,hashlib,json
from pathlib import Path


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--shards',nargs=4,type=Path,required=True)
    p.add_argument('--audit-only',action='store_true');p.add_argument('--audit-result',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    protocol=Path('configs/cached_reference_aligned_protocol.json');recipe=json.loads(protocol.read_text())
    control=Path('runs/distillation_49639916/manifest.json');base=json.loads(control.read_text())
    if base['status']!='complete' or base['updates']!=2000:raise ValueError('matched control incomplete')
    c=dict(base['config']);shards=[];seen=set();origins=set()
    for run in a.shards:
        path=run/'manifest.json';m=json.loads(path.read_text());cfg=m['config']
        if m['status']!='complete' or len(m['records'])!=128 or len(m['controls'])!=4:raise ValueError('alignment shard incomplete')
        if cfg['latent_frame']!=recipe['latent_frame'] or cfg['protocol_sha256']!=sha(protocol) or cfg['selection_sha256']!=c['selection_sha256']:raise ValueError('label protocol mismatch')
        ids={r['id'] for r in m['records']}
        if len(ids)!=128 or ids&seen:raise ValueError('duplicate labels')
        seen|=ids;origins.add(Path(cfg['source_manifest']).parent.name)
        shards.append(dict(manifest=str(path.resolve()),manifest_sha256=sha(path),labels_sha256=sha(run/'labels.h5')))
    selection=json.loads(Path(c['selection']).read_text())
    if seen!={r['id'] for r in selection['train']} or origins!={f'distill_data_{j}' for j in recipe['source_teacher_jobs']}:raise ValueError('incorrect source corpus')
    c.update(arm='cached_aligned_empirical',latent_frame=recipe['latent_frame'],label_shards=shards,
             protocol_sha256=sha(protocol),matched_control_manifest=str(control.resolve()),matched_control_manifest_sha256=sha(control))
    if a.audit_only:
        c['work_cap_seconds']=780
    else:
        if a.audit_result is None:raise ValueError('full reconstruction audit required')
        audit=json.loads(a.audit_result.read_text())
        if audit['status']!='complete' or not audit['training_gate_passed'] or audit['label_shards']!=shards:raise ValueError('aligned reconstruction gate closed')
        c.update(audit_result=str(a.audit_result.resolve()),audit_result_sha256=sha(a.audit_result))
        profile=Path(c['profile_result']);capacity=json.loads(profile.read_text())
        if sha(profile)!=c['profile_result_sha256'] or capacity['status']!='complete' or capacity['max_reserved_gib']>110:raise ValueError('unchanged workload capacity gate failed')
    if a.audit_only:a.output.write_text(json.dumps(c,indent=2)+'\n')
    else:
        for arm in recipe['arms']:
            c['arm']=arm;a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
