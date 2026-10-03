"""Provenance and geometry gates for cached-latent fragment training data."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit(c):
    for key in ('protocol','candidates','selection','source_manifest','backbones','decoder_checkpoint','historical_fragments'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed broad pilot source '+key)
    spec=json.loads(Path(c['protocol']).read_text());bm=json.loads(Path(c['candidates']).read_text());sel=json.loads(Path(c['selection']).read_text());sm=json.loads(Path(c['source_manifest']).read_text())
    if spec!=c['spec'] or bm['status']!='complete' or sm['status']!='complete' or sm['expected']!=64 or sm['selection_sha256']!=c['selection_sha256'] or sel['candidate_manifest_sha256']!=c['candidates_sha256'] or sel['dataset']!=c['cache'] or bm['source']!=c['cache']:raise ValueError('Unqualified source pilot')
    rows=sel['train'];ids=[r['id'] for r in rows]
    if ids!=bm['pilot_ids'] or len(ids)!=64 or len(set(ids))!=64 or {b:sum(r['bucket']==b for r in rows) for b in (128,256,384,512)}!={b:16 for b in (128,256,384,512)} or len(sm['records'])!=64 or {r['id'] for r in sm['records']}!=set(ids):raise ValueError('Changed pilot inventory')
    selected={r['id']:r for r in bm['selected']};verified={r['id']:r for r in sm['records']}
    with h5py.File(c['cache']) as cache,h5py.File(c['backbones']) as bb:
        for row in rows:
            ident=row['id'];r=verified[ident];maps=r['residue_map'];g=cache['train/'+ident]
            if row!=selected[ident] or r['sequence_sha256']!=row['sequence_sha256'] or sha(r['source_pdb'])!=r['source_sha256'] or r['source_ca_rmsd']>.02 or len(maps)!=row['length'] or len({tuple(x) for x in maps})!=len(maps):raise ValueError('Changed source identity')
            if any(x[0]!=y[0] or x[1]+1!=y[1] or x[2]!=' ' or y[2]!=' ' for x,y in zip(maps,maps[1:])):raise ValueError('Noncontiguous source mapping')
            if str(g.attrs['sequence'])!=row['sequence'] or str(bb[ident].attrs['sequence'])!=row['sequence']:raise ValueError('Changed cached/source sequence')
            for key in ('z','ca_coords'):
                value=g[key][:]
                if not np.isfinite(value).all() or hashlib.sha256(value.tobytes()).hexdigest()!=row['array_sha256'][key]:raise ValueError('Changed cached array')
    return rows


def qualify(records,controls,spec):
    if len(records)!=64 or len(controls)!=72:raise ValueError('Incomplete pilot evidence')
    values=[r[k] for r in records for k in ('source_ca_error','full_encoding_rmse','decoded_ca_rmsd')]+[v for r in controls for v in r.values() if isinstance(v,(float,int))]+[q[k] for r in records for q in r['fragments'] for k in ('motif_ca_rmsd','motif_drms')]
    if not np.isfinite(values).all():raise ValueError('Nonfinite pilot evidence')
    if any(r['source_ca_error']>spec['source_ca_error_max'] or r['full_encoding_rmse']>spec['full_encoding_rmse_max'] for r in records):raise ValueError('Source/latent correspondence failed')
    for r in controls:
        if r['kind']=='repeat':
            if r['ca_rmsd']>.01 or r['ca_lddt']<.999:raise ValueError('Decoder repeat failed')
        elif r['latent_max_abs']>(1e-5 if r['kind']=='historical' else 1e-4) or r.get('coordinate_max_abs',0)>1e-4:raise ValueError('Historical/pose control failed')
    endpoint=sum(r['source_valid'] and r['decoded_valid'] and r['decoded_ca_rmsd']<=spec['decoded_ca_rmsd_max'] for r in records)
    fragments=[q for r in records for q in r['fragments']]
    if len(fragments)!=576:raise ValueError('Incomplete fragment inventory')
    qualified=sum(q['motif_ca_rmsd']<=.5 and q['motif_drms']<=.5 for q in fragments)
    return dict(qualified_endpoints=endpoint,qualified_fragment_roundtrips=qualified,data_gate_passed=endpoint/64>=spec['minimum_qualified_fraction'] and qualified/576>=spec['minimum_fragment_roundtrip_fraction'])
