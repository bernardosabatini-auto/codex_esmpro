"""Recompute frame qualification on CPU after allocation release."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from context_refresh_frame_core import audit,frame_metrics,frame_gate
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];gc,parent=audit(c);b=c['base']
    basic=dict(manifest_path=str(mp.resolve()),manifest_sha256=sha(mp),protocol_sha256=sha(c['protocol']))
    if m['status']!='complete':return dict(basic,status='failed',qualified=False,error=m.get('error'))
    ids=[r['id'] for r in c['selected']];wanted={(a,i) for a in ('parent','native_direct') for i in ids}
    if (m['training_updates_executed'] or len(m['controls'])!=8 or len(m['timing'])!=8
            or {(r['arm'],r['target_id']) for r in m['controls']}!=wanted
            or {(r['arm'],r['target_id']) for r in m['timing']}!=wanted
            or m['initial_weights']!=m['final_weights'] or m['initial_weights']['decoder']!=parent['frozen_original']
            or m['peak_reserved_GiB']>75 or m['elapsed_seconds']>480 or m['predictions_sha256']!=sha(run/'predictions.h5')):
        raise ValueError('Incomplete frame preflight')
    rows=[];max_replay=0.
    with h5py.File(run/'predictions.h5') as f,h5py.File(b['source_predictions']) as prior,h5py.File(b['noise_source']) as noise:
        if set(f)!={'parent','native_direct','noise'} or any(set(f[a])!=set(ids) for a in f):raise ValueError('Changed frame inventory')
        for row in c['selected']:
            ident=row['id']
            if not np.array_equal(f['noise/'+ident][:],noise['noise/'+ident][:]):raise ValueError('Changed fixed noises')
            for arm in ('parent','native_direct'):
                g=f[arm+'/'+ident];ref=prior[arm+'/'+ident+'/backbone'][:]
                if set(g)!={'input','original_replay','latent','backbone'}:raise ValueError('Missing frame artifacts')
                expected=ref-ref.mean((1,2),keepdims=True)
                if g['input'].shape!=ref.shape or np.max(np.abs(g['input'][:]-expected))>1e-4:raise ValueError('Changed centered input')
                z=g['latent'][:]
                if z.shape!=(4,row['length'],8) or not np.isfinite(z).all() or np.max(np.abs(z.mean(-1)))>1e-4 or np.max(z.var(-1))>1.0001:
                    raise ValueError('Invalid normalized full-chain context')
                error=float(np.max(np.abs(g['original_replay'][:]-ref)));max_replay=max(max_replay,error)
                logged=next(r for r in m['controls'] if (r['arm'],r['target_id'])==(arm,ident))
                if error>1e-5 or error!=logged['max_abs']:raise ValueError('Changed original decoder replay')
                rows.extend(dict(r,arm=arm,target_id=ident,bucket=row['bucket']) for r in frame_metrics(g['backbone'][:],ref))
    if rows!=m['rows'] or frame_gate(rows)!=m['frame_qualified']:raise ValueError('Independent frame gate disagrees')
    summary=[]
    for arm in ('parent','native_direct'):
        rr=[r for r in rows if r['arm']==arm]
        summary.append(dict(arm=arm,samples=16,coarse_valid=sum(r['coarse_valid'] for r in rr),
            reconstruction_pass=sum(r['reconstruction_pass'] for r in rr),frame_pass=sum(r['frame_pass'] for r in rr),
            mean_proper_ca_rmsd=float(np.mean([r['proper_ca_rmsd'] for r in rr])),
            mean_centered_ca_rmsd=float(np.mean([r['centered_ca_rmsd'] for r in rr]))))
    return dict(basic,status='complete',qualified=frame_gate(rows),numerically_qualified=True,summary=summary,rows=rows,
        original_replay_max_abs=max_replay,predictions_sha256=sha(run/'predictions.h5'),
        gpu_elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],
        scope='Encoder/frame preflight only. Qualification permits the planned four-protein three-round context-refresh profile, not full-panel expansion or refolds.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    visible={k:v for k,v in d.items() if k!='rows'}
    a.output.with_suffix('.md').write_text('# Whole-context encoder/frame preflight\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
