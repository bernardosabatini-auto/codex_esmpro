"""Load the unchanged, certified aligned labels without another data copy."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np,torch
from prepare_overfit import sha


def metadata(c):
    for name in ('corpus_inventory','reconstruction_certificate','protocol'):
        if sha(c[name])!=c[name+'_sha256']:raise ValueError('changed '+name)
    inventory=json.loads(Path(c['corpus_inventory']).read_text())
    certificate=json.loads(Path(c['reconstruction_certificate']).read_text())
    if certificate['status']!='complete' or not certificate['reconstruction_gate_passed'] or certificate['inventory_sha256']!=c['corpus_inventory_sha256'] or sha(certificate['audit'])!=certificate['audit_sha256']:
        raise ValueError('reconstruction certificate failed or changed')
    rows=inventory['targets']
    if inventory['status']!='complete' or len(rows)!=122 or len({r['id'] for r in rows})!=122 or len({r['family'] for r in rows})!=122:raise ValueError('expected122 distinct eligible families')
    if sha(inventory['selection'])!=inventory['selection_sha256']:raise ValueError('selection changed')
    selection=json.loads(Path(inventory['selection']).read_text());train={r['id'] for r in selection['train']};tuning={r['family'] for r in selection['tuning']}
    if not {r['id'] for r in rows}<=train or {r['family'] for r in rows}&tuning:raise ValueError('training/tuning split violation')
    return inventory


def load(c):
    inventory=metadata(c);records={};buckets={k:[] for k in (128,256,384,512)}
    if c['arm']!='aligned_teacher':raise ValueError('expanded certificate only covers aligned labels')
    sources={(r['source_labels'],r['source_labels_sha256']) for r in inventory['targets']}
    for path,expected in sources:
        if sha(path)!=expected:raise ValueError('source label arrays changed')
    with h5py.File(inventory['embedding_cache']) as cache:
        for r in inventory['targets']:
            ident=r['id'];n=r['length'];record=dict(r,state=r['state_definition'])
            with h5py.File(r['source_labels']) as labels:
                g=labels[ident]
                if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('label sequence mismatch')
                for source,target in (('reference_z','reference_z'),('reference_backbone','reference_backbone'),('teacher_z','teacher_z_aligned'),('teacher_backbone','teacher_backbone')):
                    value=g[source][:]
                    if not np.isfinite(value).all():raise ValueError('nonfinite training array')
                    record[target]=torch.from_numpy(value)
                record['valid_indices']=np.flatnonzero(g['coarse_valid'][:])
            e=cache['train'][ident]
            if e.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence mismatch')
            value=e['80'][:]
            if value.shape!=(n,2560) or not np.isfinite(value).all():raise ValueError('invalid embeddings')
            if hashlib.sha256(value.tobytes()).hexdigest()!=c['embedding_arrays_sha256'][ident]:raise ValueError('embedding values changed')
            if not np.array_equal(record['valid_indices'],record['state']['teacher_indices']) or record['teacher_z_aligned'].shape!=(16,n,8) or record['teacher_backbone'].shape!=(16,n,4,3):raise ValueError('invalid teacher/state shapes')
            record['esm']=torch.from_numpy(value);records[ident]=record;buckets[r['bucket']].append(ident)
    return records,buckets
