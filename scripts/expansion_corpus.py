"""Read a fully certified larger corpus, preserving old labels and fixed panel."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np,torch
from prepare_overfit import sha


def metadata(c):
    for key in ('corpus_inventory','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    inv=json.loads(Path(c['corpus_inventory']).read_text());rows=inv['targets']
    if inv['status']!='complete' or not inv['reconstruction_gate_passed'] or len(rows)<=122 or len({r['id'] for r in rows})!=len(rows) or len({r['family'] for r in rows})!=len(rows):raise ValueError('invalid expanded training certificate')
    if c['evaluation_ids']!=inv['evaluation_ids'] or len(c['evaluation_ids'])!=64 or not set(c['evaluation_ids'])<={r['id'] for r in rows}:raise ValueError('changed fixed capacity panel')
    for key in ('selection','old_inventory','old_reconstruction_certificate','protocol'):
        if sha(inv[key])!=inv[key+'_sha256']:raise ValueError('changed certificate source')
    for shard in inv['source_shards']:
        if sha(shard['manifest'])!=shard['manifest_sha256']:raise ValueError('changed label generation manifest')
    if c['arm']!='aligned_teacher' or c.get('label_distribution')!='balanced' or c.get('local_geometry') or c.get('trainable_tail_blocks') is not None:raise ValueError('larger-corpus test changes data only')
    return inv


def load(c):
    inv=metadata(c);records={};buckets={k:[] for k in (128,256,384,512)}
    for path,expected in {(r['source_labels'],r['source_labels_sha256']) for r in inv['targets']}:
        if sha(path)!=expected:raise ValueError('training labels changed')
    embeddings={};labels={}
    try:
        for row in inv['targets']:
            ident=row['id'];n=row['length'];ep=row['embedding_cache'];lp=row['source_labels']
            if ep not in embeddings:embeddings[ep]=h5py.File(ep)
            if lp not in labels:labels[lp]=h5py.File(lp)
            e=embeddings[ep]['train'][ident];g=labels[lp][ident]
            if e.attrs['sequence_sha256']!=row['sequence_sha256'] or g.attrs['sequence_sha256']!=row['sequence_sha256']:raise ValueError('sequence identity changed')
            record=dict(row,state=row['state_definition'])
            for source,target in (('reference_z','reference_z'),('reference_backbone','reference_backbone'),('teacher_z','teacher_z_aligned'),('teacher_backbone','teacher_backbone')):
                value=g[source][:]
                if not np.isfinite(value).all():raise ValueError('nonfinite labels')
                record[target]=torch.from_numpy(value)
            record['valid_indices']=np.flatnonzero(g['coarse_valid'][:]);value=e['80'][:]
            if value.shape!=(n,2560) or not np.isfinite(value).all() or hashlib.sha256(value.tobytes()).hexdigest()!=row['embedding_array_sha256']:raise ValueError('embedding array changed')
            if not np.array_equal(record['valid_indices'],row['state_definition']['teacher_indices']) or record['teacher_z_aligned'].shape!=(16,n,8):raise ValueError('label state mismatch')
            record['esm']=torch.from_numpy(value);records[ident]=record;buckets[row['bucket']].append(ident)
    finally:
        for handle in list(embeddings.values())+list(labels.values()):handle.close()
    return records,buckets


def evaluation_records(records,config):
    ids=config.get('evaluation_ids')
    if ids is None:return records
    if config.get('corpus_kind')!='expansion' or len(ids)!=64 or len(set(ids))!=64 or not set(ids)<=set(records):raise ValueError('invalid fixed training-capacity panel')
    if {records[i]['bucket'] for i in ids}!={128,256,384,512}:raise ValueError('capacity panel misses length controls')
    return {ident:records[ident] for ident in ids}
