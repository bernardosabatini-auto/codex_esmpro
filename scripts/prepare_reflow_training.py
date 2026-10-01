"""Freeze complete paired sampler labels and a matched training recipe."""
import argparse,hashlib,json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--shards',type=Path,nargs='+',required=True);p.add_argument('--profile-only',action='store_true');p.add_argument('--profile-result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    protocol=Path('configs/reflow_protocol.json').resolve();selection=Path('runs/layer_probe/frozen.json').resolve();s=json.loads(selection.read_text());seen=set();shards=[];origins=set();checkpoints=set()
    for run in a.shards:
        path=run/'manifest.json';m=json.loads(path.read_text());c=m['config']
        if m['status']!='complete' or c['protocol_sha256']!=sha(protocol) or c['selection_sha256']!=sha(selection) or len(m['controls'])!=4:raise ValueError('pair generation not eligible')
        ids={r['id'] for r in m['records']}
        if ids!={r['id'] for r in s['train'][c['shard']::4]} or seen&ids:raise ValueError('pair coverage mismatch')
        seen|=ids;origins.add(c['shard']);checkpoints.add(m['checkpoint']['sha256'])
        shards.append(dict(manifest=str(path.resolve()),manifest_sha256=sha(path),pairs_sha256=sha(run/'pairs.h5')))
    if len(checkpoints)!=1 or (not a.profile_only and (origins!={0,1,2,3} or len(seen)!=512)):raise ValueError('incomplete/mixed pair corpus')
    c=dict(selection=str(selection),selection_sha256=sha(selection),embedding_cache=str(Path('runs/layer_probe_49625917/embeddings.h5').resolve()),protocol=str(protocol),protocol_sha256=sha(protocol),pair_shards=shards,seed=2026100151,evaluation_seed=2026100109,batches={'128':32,'256':16,'384':8,'512':8},learning_rate=1e-5,ema_decay=.99,warmup_updates=100,updates=40 if a.profile_only else 2000,evaluation_steps=[40] if a.profile_only else [500,2000],work_cap_seconds=780 if a.profile_only else 5700,profile_only=a.profile_only)
    if not a.profile_only:
        if a.profile_result is None:raise ValueError('training profile required')
        profile=json.loads(a.profile_result.read_text())
        if profile['status']!='complete' or not profile['profile_only'] or profile['max_reserved_gib']>110:raise ValueError('capacity gate failed')
        c.update(profile_result=str(a.profile_result.resolve()),profile_result_sha256=sha(a.profile_result))
    for arm in (['reflow_paired'] if a.profile_only else ['reflow_paired','reflow_independent']):
        c['arm']=arm;a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
