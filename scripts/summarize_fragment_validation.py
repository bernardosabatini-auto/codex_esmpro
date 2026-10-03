"""Audit all fresh samples and keep overlapping cohorts explicitly separate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_validation_core import audit_config,raw_rows,view_rows
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];audit_config(c);spec=c['spec']
    if m['training_updates'] or sha(run/'predictions.h5')!=m['predictions_sha256']:raise ValueError('Changed fresh outputs')
    expected={(kind,arm,i) for kind in ('historical','same_batch_repeat','pose') for arm in c['models'] for i in c['target_ids']}
    if len(m['controls'])!=len(expected) or {(r['kind'],r['arm'],r['target_id']) for r in m['controls']}!=expected:raise ValueError('Incomplete controls')
    for r in m['controls']:
        if not np.isfinite(r['latent_max_abs']) or r['latent_max_abs']>(1e-4 if r['kind']=='pose' else 1e-5):raise ValueError('Latent control failed')
        if r['kind']=='historical' and (r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['same_validity'] or not r['same_strict_decisions']):raise ValueError('Historical decisions failed')
    records=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['fragments']) as fr:
        if set(f)!=set(c['models'])|{'historical'} or set(f['historical'])!=set(c['models']):raise ValueError('Changed arm inventory')
        for arm,source in c['models'].items():
            if set(f[arm])!=set(c['target_ids']) or set(f['historical/'+arm])!=set(c['target_ids']):raise ValueError('Changed target inventory')
            with h5py.File(source['historical_predictions']) as old:
                for ident in c['target_ids']:
                    v=fr['development/'+ident];q=v['conditions/'+spec['condition']];n=int(v.attrs['length']);samples=16 if ident==spec['focus_id'] else 4;g=f[arm+'/'+ident];bb=g['backbone'][:];z=g['latent'][:]
                    if bb.shape!=(samples,n,4,3) or z.shape!=(samples,n,8) or not np.isfinite(bb).all() or not np.isfinite(z).all():raise ValueError('Missing/invalid fresh sample')
                    for key,limit in [('same_batch_repeat',1e-5),('pose',1e-4)]:
                        if g[key].shape!=z[:4].shape or np.max(abs(g[key][:]-z[:4]))>limit:raise ValueError('Stored sampling control failed')
                    hg=f['historical/'+arm+'/'+ident];reference=old['development/conditioned/'+ident];hb=hg['backbone'][:];rb=reference['backbone'][:]
                    if hb.shape!=(4,n,4,3) or np.max(abs(hg['latent'][:]-reference['latent'][:]))>1e-5:raise ValueError('Stored historical mismatch')
                    for x,y in zip(hb,rb):
                        metric=ca_metrics(x[:,1],y[:,1])
                        if metric['ca_rmsd']>.2 or metric['ca_lddt']<.99:raise ValueError('Stored historical geometry failed')
                    args=(q['fragment'][:],int(q.attrs['start']),arm,ident,str(v.attrs['family']))
                    left,right=raw_rows(hb,*args),raw_rows(rb,*args)
                    if any(x[k]!=y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed')):raise ValueError('Stored historical decisions changed')
                    records.extend(raw_rows(bb,*args))
    if len(m['batches'])!=32 or {(x['arm'],x['target_id']) for x in m['batches']}!={(arm,i) for arm in c['models'] for i in c['target_ids']} or any(x['samples']!=(16 if x['target_id']==spec['focus_id'] else 4) or x['peak_reserved_GiB']>75 for x in m['batches']):raise ValueError('Changed generation inventory/resource limit')
    summaries=[]
    for arm in c['models']:
        for view in ('whole_panel','focus'):
            rr=view_rows(records,arm,view,spec['focus_id'])
            if len(rr)!=(64 if view=='whole_panel' else 16):raise ValueError('Changed denominator')
            summaries.append(dict(arm=arm,view=view,samples=len(rr),families=len({r['family'] for r in rr}),valid=sum(r['coarse_valid'] for r in rr),strict_raw=sum(r['raw_gate_passed'] for r in rr),families_with_strict_raw=len({r['family'] for r in rr if r['raw_gate_passed']}),mean_motif_ca_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr]))))
    return dict(status='complete',manifest_sha256=sha(path),predictions_sha256=m['predictions_sha256'],unique_generated_samples=len(records),summaries=summaries,records=records,controls=m['controls'],timing=m['batches'],elapsed_seconds=m['elapsed_seconds'],interpretation=spec['scope']+' Views overlap by four samples perarm; raw matches require refolding.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fresh-noise fragment validation\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('records','controls','timing')},indent=2)+'\n```\n')

if __name__=='__main__':main()
