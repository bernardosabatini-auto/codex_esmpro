import argparse,json
from pathlib import Path
import h5py,numpy as np
from broad_codec_batch_core import items
from latentfold.metrics import ca_metrics
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),profile_qualified=False)
    c=m['config'];spec=c['spec'];data=items(c);controls=[];short=[];failures=[]
    if m['training_updates_executed'] or sha(run/'outputs.h5')!=m['outputs_sha256'] or max(r['peak_reserved_GiB'] for r in m['batches'])>spec['max_reserved_GiB']:raise ValueError('Changed codec batch output')
    with h5py.File(run/'outputs.h5') as out:
        leaves=[]
        out.visititems(lambda name,obj:leaves.append(name) if isinstance(obj,h5py.Group) and 'backbone' in obj else None)
        if set(leaves)!={r['key'] for r in data}:raise ValueError('Changed stored codec inventory')
        for r in data:
            g=out[r['key']];n=len(r['backbone']);values={k:g[k][:] for k in ('encoded','latent','backbone')}
            if set(g)!=set(values) or any(not np.isfinite(v).all() for v in values.values()) or values['backbone'].shape!=(n,4,3) or any(values[k].shape!=(n,8) for k in ('encoded','latent')):raise ValueError('Invalid batched codec output')
            if r['kind']=='new':
                fit=motif_fit(values['backbone'],r['backbone'],0);short.append(dict(key=r['key'],**fit,qualified=fit['motif_ca_rmsd']<=.5 and fit['motif_drms']<=.5));continue
            target='encoded' if r['kind']=='full' else 'latent';expected=r.get('expected_encoded',r.get('expected_latent'));error=float(np.max(abs(values[target]-expected)));control=dict(key=r['key'],kind=r['kind'],latent_max_abs=error)
            if error>(spec['historical_latent_max_abs'] if r['kind']=='historical' else spec['encoded_max_abs']):failures.append(dict(key=r['key'],criterion='encoder',error=error))
            if r['kind']!='historical':
                reference=r['expected_backbone'];bb=values['backbone'];metric=ca_metrics(bb[:,1],reference[:,1]);control.update(metric)
                if metric['ca_rmsd']>spec['decoded_ca_rmsd_max'] or metric['ca_lddt']<spec['decoded_ca_lddt_min']:failures.append(dict(key=r['key'],criterion='decoder',**metric))
                if r['kind']=='full':
                    decisions=[bool(backbone_geometry(x[None])['coarse_valid'][0]) and ca_metrics(x[:,1],r['backbone'][:,1])['ca_rmsd']<=1 for x in (bb,reference)]
                    if not np.array_equal(values['latent'],r['reference_latent']):raise ValueError('Cached full target changed')
                else:
                    fits=[motif_fit(x,r['backbone'],0) for x in (bb,reference)];decisions=[f['motif_ca_rmsd']<=.5 and f['motif_drms']<=.5 for f in fits]
                if decisions[0]!=decisions[1]:failures.append(dict(key=r['key'],criterion='qualification_decision'))
                control['qualification_unchanged']=decisions[0]==decisions[1]
            controls.append(control)
    if len(controls)!=644 or len(short)!=192:raise ValueError('Incomplete codec evidence')
    qualified=sum(r['qualified'] for r in short)
    return dict(status='complete',manifest_sha256=sha(path),outputs_sha256=m['outputs_sha256'],profile_qualified=not failures and qualified/192>=.9,parity_failures=failures,numerical_controls=644,short_fragment_roundtrips=192,qualified_short_roundtrips=qualified,batch_size=spec['batch_size'],peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['batches']),batch_work_seconds=sum(r['seconds'] for r in m['batches']),elapsed_seconds=m['elapsed_seconds'],controls=controls,short_records=short,scope=spec['scope']+' Timing includes192additional short crops and differs in output work from the single-item pilot; do not quote an unadjusted speedup.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Batched fragment codec qualification\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('controls','short_records','parity_failures')},indent=2)+'\n```\n')

if __name__=='__main__':main()
