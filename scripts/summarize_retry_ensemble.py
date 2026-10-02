"""Audit the complete raw/selected/attempted external ensembles before state scoring."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.ensemble_metrics import backbone_geometry


def validate_slot(draws,selection):
    slot=selection['slot'];attempts=selection['attempts'];draws=sorted(draws,key=lambda r:r['attempt'])
    if not 0<=slot<32 or not 1<=attempts<=4 or len(draws)!=attempts or [r['attempt'] for r in draws]!=list(range(attempts)) or any(r['draw']!=slot+32*r['attempt'] or r['coarse_valid'] not in (0,1) for r in draws):raise ValueError('Incomplete or reordered attempts')
    hits=[r for r in draws if r['coarse_valid']]
    if hits:
        if len(hits)!=1 or hits[0]!=draws[-1] or selection['exhausted'] or selection['selected_draw']!=hits[0]['draw']:raise ValueError('Not first-valid selection')
    elif attempts!=4 or not selection['exhausted'] or selection['selected_draw']!=slot:raise ValueError('Incorrect exhausted fallback')
    return draws[0]['draw'],selection['selected_draw']


def analyze(m,run):
    if m['status']!='complete' or m['training_updates_executed']!=0:raise ValueError('Incomplete inference')
    c=m['config']
    for key in ('protocol','panel','native_manifest','capacity_report','parent_manifest','parent_scores'):
        if c.get(key) and sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    rows={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']}
    if len(rows)!=48 or len({r['family'] for r in rows.values()})!=48 or c['noise_arms']!=['raw','latent'] or c['samples']!=32 or c['max_attempts']!=4:raise ValueError('Wrong panel/recipe')
    if len(m['targets'])!=48 or {r['id'] for r in m['targets']}!=set(rows):raise ValueError('Incomplete targets')
    controls=m['controls']
    if len(controls)!=48 or {r['target_id'] for r in controls}!=set(rows) or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('Failed batch controls')
    parent=m['parent_controls']
    if c.get('parent_predictions'):
        if len(parent)!=48 or {r['target_id'] for r in parent}!=set(rows) or any(not np.isfinite(r[k]) for r in parent for k in ('max_ca_rmsd','min_ca_lddt')) or any(r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['validity_identical'] for r in parent):raise ValueError('Failed raw parent controls')
    elif parent:raise ValueError('Unexpected raw parent controls')
    expected={(i,k) for i in rows for k in range(32)};key=lambda r:(r['target_id'],r['slot'])
    if len(m['selections'])!=1536 or {key(r) for r in m['selections']}!=expected or any(key(r) not in expected for r in m['draws']):raise ValueError('Incomplete/extra output slots')
    byslot={k:[] for k in expected}
    for r in m['draws']:byslot[key(r)].append(r)
    choices={}
    for s in m['selections']:choices[key(s)]=validate_slot(byslot[key(s)],s)
    batches=m['batches'];batch_keys=[(r['target_id'],r['attempt']) for r in batches]
    if len(batch_keys)!=len(set(batch_keys)) or {i for i,a in batch_keys if a==0}!=set(rows) or any(i not in rows or not 0<=a<4 for i,a in batch_keys):raise ValueError('Incorrect batch timing coverage')
    for r in batches:
        if r['batch']!=sum(x['target_id']==r['target_id'] and x['attempt']==r['attempt'] for x in m['draws']) or any(not np.isfinite(r[k]) or r[k]<=0 for k in ('seconds','peak_reserved_bytes')):raise ValueError('Invalid batch cost accounting')
    if sum(r['batch'] for r in batches)!=len(m['draws']):raise ValueError('Missing attempt timings')
    with h5py.File(run/'predictions.h5') as h:
        if set(h)!=set(rows):raise ValueError('Missing prediction families')
        for ident,row in rows.items():
            if set(h[ident])!={f"cfg{c['primary_guidance']}"}:raise ValueError('Unexpected guidance')
            g=h[ident][f"cfg{c['primary_guidance']}"]
            if set(g)!={'raw','latent','attempts'}:raise ValueError('Missing raw/selected/attempt evidence')
            indices=g['attempts']['draw_indices'][:];bb=g['attempts']['backbone'][:];ds=[r for r in m['draws'] if r['target_id']==ident]
            if len(indices)!=len(ds) or len(set(indices))!=len(indices) or bb.shape!=(len(indices),row['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Incomplete attempted backbones')
            if set(indices)!={r['draw'] for r in ds}:raise ValueError('Attempt indices changed')
            validity=np.concatenate([backbone_geometry(bb[k:k+32])['coarse_valid'] for k in range(0,len(bb),32)])
            mapping={int(k):j for j,k in enumerate(indices)}
            if any(bool(validity[mapping[r['draw']]])!=bool(r['coarse_valid']) for r in ds):raise ValueError('Stored validity differs from coordinates')
            for mode,pos in [('raw',0),('latent',1)]:
                wanted=[choices[(ident,k)][pos] for k in range(32)];pairs=np.stack([wanted,np.zeros(32,dtype=int)],axis=1)
                if not np.array_equal(g[mode]['seed_indices'][:],pairs) or not np.array_equal(g[mode]['backbone'][:],bb[[mapping[k] for k in wanted]]):raise ValueError('Output differs from declared selected draw')
    initial=sum(not r['coarse_valid'] for r in m['draws'] if r['attempt']==0);left=sum(r['exhausted'] for r in m['selections'])
    return dict(status='complete',name=c['name'],families=48,outputs=1536,attempts=len(m['draws']),initially_invalid=initial,recovered=initial-left,exhausted=left,attempts_per_output=len(m['draws'])/1536,initial_seconds=sum(r['seconds'] for r in batches if r['attempt']==0),retry_seconds=sum(r['seconds'] for r in batches if r['attempt']>0),peak_reserved_gib=max(r['peak_reserved_bytes'] for r in batches)/1024**3,manifest_sha256=sha(run/'manifest.json'),predictions_sha256=sha(run/'predictions.h5'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    d=analyze(m,run) if m['status']=='complete' else dict(status=m['status'],error=m.get('error','Incomplete'))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# External bounded retry integrity and cost','',f"Status:{d['status']}; head:{d.get('name')}.",'','All48 families and1536 output slots; first coarse-valid draw, at most four attempts, original fallback. Every attempted backbone retained. Reference-free selection, unchanged geometry rules.']
    if d['status']=='complete':lines+=['',f"Initial invalid:{d['initially_invalid']}; recovered:{d['recovered']}; exhausted:{d['exhausted']}. Attempted draws:{d['attempts']} ({d['attempts_per_output']:.5f}/output).",'',f"Initial generation:{d['initial_seconds']:.2f}s; retry generation:{d['retry_seconds']:.2f}s; peak reserved:{d['peak_reserved_gib']:.2f}GiB. These exclude ESM, loading, controls, geometry checks and disk I/O. No end-to-end speed claim.",'','Frozen state, CA and MD scoring follows on CPU for both raw and selected32. Validity alone is not diversity or generalization.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
