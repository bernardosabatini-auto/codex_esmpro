"""Freeze disjoint training-family replay and its bounded resource profile."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile-only',action='store_true');p.add_argument('--profile',type=Path);p.add_argument('--seed',type=int,choices=[2026100171,2026100181],default=2026100171);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/functional_replay_protocol.json';recipe=json.loads(protocol.read_text());native=root/'runs/layer_probe/frozen.json';corpus=root/'runs/expanded_labels_inventory.json';cache=root/'runs/layer_probe_49625917/embeddings.h5'
    native_data=json.loads(native.read_text());inventory=json.loads(corpus.read_text());used={r['family'] for r in inventory['targets']};rows=[r for r in native_data['train'] if r['family'] not in used]
    if len(rows)!=390 or len({r['family'] for r in rows})!=390 or set(r['family'] for r in rows)&used:raise ValueError('replay family overlap or wrong coverage')
    selection=dict(targets=rows,scope='All disjoint native training families; no outcomes used for selection.')
    for key,path in dict(native_selection=native,corpus_inventory=corpus,embedding_cache=cache).items():selection[key]=str(path);selection[key+'_sha256']=sha(path)
    path=root/'runs/functional_replay_selection.json';raw=json.dumps(selection,indent=2)+'\n'
    if path.exists() and path.read_text()!=raw:raise ValueError('frozen replay selection changed')
    if not path.exists():path.write_text(raw)
    jid='49814858' if a.seed==2026100171 else '49815018';c=dict(json.loads((root/f'runs/overfit_{jid}/manifest.json').read_text())['config'])
    checkpoint=root/'runs/inference_checkpoints/original459m_ema.ckpt'
    c.update(functional_replay=True,replay_protocol=str(protocol),replay_protocol_sha256=sha(protocol),replay_selection=str(path),replay_selection_sha256=sha(path),replay_checkpoint=str(checkpoint),replay_checkpoint_sha256=sha(checkpoint),profile_only=a.profile_only,updates=40 if a.profile_only else 2000,evaluation_steps=[40] if a.profile_only else [500,2000],work_cap_seconds=780 if a.profile_only else 10440,maximum_profile_gib=80)
    if a.profile_only:
        c.pop('profile_report',None);c.pop('profile_report_sha256',None)
    else:
        if not a.profile:raise ValueError('replay profile required')
        m=json.loads(a.profile.read_text());r=m.get('functional_replay',{})
        if m['status']!='complete' or not m['profile_only'] or m['max_reserved_gib']>80 or m['training_seconds']>240 or not r.get('reference_unchanged') or r.get('positive_updates',0)<30 or r.get('buckets')!=[128,256,384,512]:raise ValueError('replay profile not qualified')
        c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile))
        c['allocation_minutes']=max(120,math.ceil(1.25*(m['training_seconds']*50+1200)/60));c['work_cap_seconds']=60*c['allocation_minutes']-180
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
