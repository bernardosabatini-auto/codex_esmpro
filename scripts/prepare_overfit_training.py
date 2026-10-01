"""Bind all three capacity-test arms to one audited label corpus."""
import argparse,json
import h5py,numpy as np
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.labels.read_text());protocol=json.loads(Path(m['config']['protocol']).read_text())
    if m['status']!='complete' or not m['training_gate_passed'] or sha(m['config']['protocol'])!=m['config']['protocol_sha256']:raise ValueError('label gate failed')
    selection=json.loads(Path(m['config']['selection']).read_text())
    if sha(m['config']['selection'])!=m['config']['selection_sha256']:raise ValueError('selection changed')
    identities=[]
    with h5py.File(a.labels.parent/'labels.h5') as labels,h5py.File(m['config']['embedding_cache']) as cache,h5py.File(selection['dataset']) as original:
        for row in m['config']['targets']:
            ident=row['id'];g=labels[ident];e=cache['train'][ident]
            if g.attrs['sequence_sha256']!=row['sequence_sha256'] or e.attrs['sequence_sha256']!=row['sequence_sha256']:raise ValueError('embedding or label sequence mismatch')
            if not np.array_equal(g['esm'][:],e['80'][:]) or not np.array_equal(g['reference_z'][:],original['train'][ident]['z'][:]):raise ValueError('copied embeddings or cached reference changed')
            identities.append(ident)
    if len(identities)!=32 or len(set(identities))!=32:raise ValueError('expected32 unique training inputs')
    c={k:protocol[k] for k in ('updates','evaluation_steps','learning_rate','ema_decay','warmup_updates','seed','evaluation_seed')};c.update(label_manifest=str(a.labels.resolve()),label_manifest_sha256=sha(a.labels),protocol=m['config']['protocol'],protocol_sha256=m['config']['protocol_sha256'],batches={'128':32,'256':16,'384':8,'512':8},work_cap_seconds=6600,profile_only=False,decoder_steps=m['config'].get('decoder_steps',3))
    if a.profile is None:
        c.update(arm='aligned_teacher',updates=40,evaluation_steps=[40],profile_only=True,work_cap_seconds=480);a.output.write_text(json.dumps(c,indent=2)+'\n')
    else:
        profile=json.loads(a.profile.read_text())
        if profile['status']!='complete' or not profile['profile_only'] or profile['max_reserved_gib']>110:raise ValueError('capacity profile failed')
        c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile))
        for arm in protocol['arms']:
            c['arm']=arm;a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
