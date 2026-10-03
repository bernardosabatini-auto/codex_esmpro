"""Bind cached training-only teacher candidates without changing fragments."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit_config(c):
    for key in ('protocol','inventory','fragments','parent_manifest','decoder_checkpoint','candidates'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed augmentation source '+key)
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['parent_manifest']).read_text())
    if spec!=c['spec'] or m['status']!='complete' or Path(c['parent_manifest']).parent.name!=spec['parent'] or m['config']['fragments_sha256']!=c['fragments_sha256'] or m['config']['decoder_checkpoint_sha256']!=c['decoder_checkpoint_sha256']:raise ValueError('Changed parent or augmentation recipe')
    with h5py.File(c['fragments']) as fr,h5py.File(c['candidates']) as candidates:
        if len(fr['train'])!=128 or set(candidates)!=set(fr['train']) or set(candidates)&set(fr['development']):raise ValueError('Changed training-only coverage')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_teacher_augmentation_protocol.json';spec=json.loads(protocol.read_text());inventory=root/spec['inventory'];d=json.loads(inventory.read_text());fragments=root/spec['fragments'];parent=root/'runs'/spec['parent']/'manifest.json';m=json.loads(parent.read_text());inputs=a.output.with_suffix('.h5').resolve();c=dict(spec=spec)
    if d['status']!='complete':raise ValueError('Incomplete teacher inventory')
    for s in d['source_shards']:
        if sha(s['manifest'])!=s['manifest_sha256'] or sha(s['labels'])!=s['labels_sha256']:raise ValueError('Changed cached teacher shard')
    handles={}
    try:
        with h5py.File(fragments) as fr,h5py.File(inputs,'x') as out:
            for ident,g in fr['train'].items():
                rows=[r for r in d['records'] if r['target_id']==ident]
                if len(rows)!=9 or {r['condition'] for r in rows}!=set(g['conditions']):raise ValueError('Missing original condition')
                paths={r['source_labels'] for r in rows}
                if len(paths)!=1:raise ValueError('Ambiguous teacher source')
                path=paths.pop()
                if path not in handles:handles[path]=h5py.File(path)
                src=handles[path][ident]
                if not np.array_equal(src['reference_backbone'][:],g['reference_backbone'][:]) or not np.array_equal(src['reference_z'][:],g['reference_z'][:]):raise ValueError('Changed original target')
                group=out.create_group(ident);states=sorted({s['index'] for r in rows for s in r['eligible_states']});group.create_dataset('state_indices',data=np.asarray(states,dtype=np.int64));group.attrs['family']=g.attrs['family'];group.attrs['length']=g.attrs['length'];group.attrs['source_labels']=path
                if states:
                    group.create_dataset('teacher_z',data=src['teacher_z'][states]);group.create_dataset('teacher_backbone',data=src['teacher_backbone'][states])
                for r in rows:
                    q=g['conditions/'+r['condition']]
                    if r['length']!=g.attrs['length'] or r['motif_start']!=q.attrs['start'] or r['motif_length']!=len(q['fragment']):raise ValueError('Changed isolated fragment')
                    group.create_dataset('conditions/'+r['condition'],data=np.asarray([states.index(s['index']) for s in r['eligible_states']],dtype=np.int64))
    finally:
        for f in handles.values():f.close()
    for key,path in [('protocol',protocol),('inventory',inventory),('fragments',fragments),('parent_manifest',parent),('decoder_checkpoint',Path(m['config']['decoder_checkpoint'])),('candidates',inputs)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Bound original128proteins and cached candidate states')


if __name__=='__main__':main()
