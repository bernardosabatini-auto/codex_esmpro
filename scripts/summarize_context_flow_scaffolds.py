"""All-sample raw capacity screen; never equate latent loss with designability."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from context_flow_generation import audit
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from fragment_repaint_teacher_core import eligibility
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text())
    if m['config'].get('context_normalization_profile'):
        from context_normalization_profile import analyze as normalization_audit
        return normalization_audit(run)
    if m['status']!='complete':return dict(status='failed',error=m.get('error'))
    c=m['config'];audit(c)
    if m['predictions_sha256']!=sha(run/'predictions.h5') or m['training_updates_executed']!=0:
        raise ValueError('Changed generated archive')
    expected={(arm,r['id']) for arm in c['spec']['arms'] for r in c['selected']}
    if len(m['batches'])!=64 or {(r['arm'],r['target_id']) for r in m['batches']}!=expected:
        raise ValueError('Dropped generation')
    controls={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
    if len(m['controls'])!=4 or {r['target_id'] for r in m['controls']}!=controls:
        raise ValueError('Missing historical controls')
    lookup={r['id']:r for r in c['evaluation_rows']};records=[];diversity=[]
    codes={arm:np.load(path,allow_pickle=False).reshape(32,4,20,8) for arm,path in c['codes'].items()}
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['fragments']) as fr,h5py.File(c['oracle_predictions']) as old,h5py.File(c['baseline_predictions']) as base:
        if set(f)!={'controls',*c['spec']['arms']} or set(f['controls'])!=controls:
            raise ValueError('Wrong groups')
        for ident in controls:
            q=fr['train/'+ident+'/conditions/c20_center'];g=f['controls/'+ident];st=int(q.attrs['start'])
            gap=float(np.max(abs(g['latent'][:]-old['new/'+ident+'/latent'][:])))
            if gap>1e-5:raise ValueError('Historical latent replay failed')
            check=check_backbones(g['backbone'][:],old['new/'+ident+'/backbone'][:],q['fragment'][:],st,ident)
            logged=next(r for r in m['controls'] if r['target_id']==ident)
            if gap!=logged['latent_max_abs'] or any(logged[k]!=v for k,v in check.items()):
                raise ValueError('Historical report mismatch')
        for arm in c['spec']['arms']:
            if set(f[arm])!={r['id'] for r in c['selected']}:raise ValueError('Missing targets')
        for row in c['selected']:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start']);n=row['length']
            if st!=lookup[ident]['start'] or str(q.attrs['sequence'])!=lookup[ident]['sequence']:
                raise ValueError('Changed original motif')
            for arm in c['spec']['arms']:
                g=f[arm+'/'+ident];used=np.zeros((4,n,8),np.float32)
                used[:,st:st+20]=codes[arm][lookup[ident]['index']]
                if (g['latent'].shape!=(4,n,8) or g['backbone'].shape!=(4,n,4,3)
                        or not np.array_equal(used,g['target'][:]) or not np.isfinite(g['backbone'][:]).all()
                        or not np.isfinite(g['latent'][:]).all()):raise ValueError('Changed learned input or inventory')
                bb=g['backbone'][:]
                rr=raw_rows(bb,q['fragment'][:],st,arm,ident,row['family'])
                records.extend(dict(r,bucket=row['bucket']) for r in rr)
                keep=np.ones(n,bool);keep[st:st+20]=False
                for i in range(4):
                    for j in range(i+1,4):
                        scores=ca_metrics(bb[i,keep,1],bb[j,keep,1])
                        diversity.append(dict(arm=arm,target_id=ident,slots=[i,j],
                            both_raw=rr[i]['raw_gate_passed'] and rr[j]['raw_gate_passed'],
                            scaffold_ca_rmsd=scores['ca_rmsd']))
            records.extend(dict(r,bucket=row['bucket']) for r in raw_rows(base['new/'+ident+'/backbone'][:],q['fragment'][:],st,'parent',ident,row['family']))
    summaries={arm:eligibility([r for r in records if r['arm']==arm]) for arm in (*c['spec']['arms'],'parent')}
    if summaries['parent']['raw']!=25 or summaries['parent']['valid']!=128:raise ValueError('Parent outcomes changed')
    for arm,r in summaries.items():
        r['mean_motif_rmsd']=float(np.mean([x['motif_ca_rmsd'] for x in records if x['arm']==arm]))
    return dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],summary=summaries,
                records=records,diversity=diversity,controls=4,control_samples=16,designability_tested=False,
                generation_seconds=sum(r['seconds'] for r in m['batches']),elapsed_seconds=m['elapsed_seconds'],
                peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['batches']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    short={k:v for k,v in d.items() if k not in ('records','diversity')}
    a.output.with_suffix('.md').write_text('# Context-code scaffold generation\n\n```json\n'+json.dumps(short,indent=2)+'\n```\n')
    print(json.dumps(short))


if __name__=='__main__':main()
