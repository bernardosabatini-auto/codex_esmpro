import argparse,json
from pathlib import Path
import h5py,numpy as np
from extra_fragment_validation_core import audit_config,load_conditions
from fragment_validation_core import raw_rows
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec=audit_config(c);records=[];wanted={('historical',i) for i in c['control_ids']}|{(k,i) for k in ('same_batch_repeat','pose') for i in c['target_ids']}
    if m['training_updates_executed'] or sha(run/'predictions.h5')!=m['predictions_sha256'] or len(m['controls'])!=132 or {(r['kind'],r['target_id']) for r in m['controls']}!=wanted or len(m['batches'])!=64 or {r['target_id'] for r in m['batches']}!=set(c['target_ids']):raise ValueError('Changed generation inventory')
    for r in m['controls']:
        if not np.isfinite(r['latent_max_abs']) or r['latent_max_abs']>(1e-4 if r['kind']=='pose' else 1e-5):raise ValueError('Numerical control failed')
        if r['kind']=='historical' and (r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['same_decisions']):raise ValueError('Historical control failed')
    for r in m['batches']:
        if r['samples']!=4 or r['peak_reserved_GiB']>75:raise ValueError('Changed sampling resources')
    new=load_conditions(c['fragments'],c['target_ids'],spec.get('condition','f30_center'));history=load_conditions(c['historical_fragments'],c['control_ids'])
    with h5py.File(run/'predictions.h5') as out,h5py.File(c['historical_predictions']) as old:
        if set(out)!={'new','historical'} or set(out['new'])!=set(new) or set(out['historical'])!=set(history):raise ValueError('Changed stored inventory')
        for ident,item in history.items():
            g=out['historical/'+ident];reference=old['development/conditioned/'+ident];bb=g['backbone'][:];rb=reference['backbone'][:]
            if np.max(abs(g['latent'][:]-reference['latent'][:]))>1e-5:raise ValueError('Stored historical latent changed')
            for x,y in zip(bb,rb):
                metric=ca_metrics(x[:,1],y[:,1])
                if metric['ca_rmsd']>.2 or metric['ca_lddt']<.99:raise ValueError('Stored historical coordinates changed')
            args=(item['fragment'],item['start'],c['arm'],ident,item['family']);left,right=raw_rows(bb,*args),raw_rows(rb,*args)
            if any(x[k]!=y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed')):raise ValueError('Historical decisions changed')
        for ident,item in new.items():
            g=out['new/'+ident];z=g['latent'][:];bb=g['backbone'][:];n=item['length']
            if z.shape!=(4,n,8) or bb.shape!=(4,n,4,3) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Missing or invalid new sample')
            for k,tol in [('same_batch_repeat',1e-5),('pose',1e-4)]:
                if g[k].shape!=z.shape or np.max(abs(g[k][:]-z))>tol:raise ValueError('Stored repeat/pose failed')
            records.extend(raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family']))
    summaries=[]
    for cohort in ('all','short','long'):
        rr=[r for r in records if cohort=='all' or (r['length']<=256 if cohort=='short' else r['length']>256)]
        if len(rr)!=(256 if cohort=='all' else 128):raise ValueError('Changed stratified denominator')
        summaries.append(dict(cohort=cohort,samples=len(rr),families=len({r['family'] for r in rr}),valid=sum(r['coarse_valid'] for r in rr),raw_matches=sum(r['raw_gate_passed'] for r in rr),mean_motif_ca_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr]))))
    return dict(status='complete',arm=c['arm'],manifest_sha256=sha(path),predictions_sha256=m['predictions_sha256'],summaries=summaries,records=records,controls=132,timing=m['batches'],elapsed_seconds=m['elapsed_seconds'],scope=spec['scope']+' Raw retention does not establish designability.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Additional-family conditional generation\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('records','timing')},indent=2)+'\n```\n')

if __name__=='__main__':main()
