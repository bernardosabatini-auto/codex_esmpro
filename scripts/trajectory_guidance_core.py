"""Immutable source binding and CPU audits for one mid-flow guidance pilot."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np
from context_flow_generation import identity,audit_worker
from verified_sources import VerifiedSources
from prepare_overfit import sha
from fragment_validation_core import raw_rows


def prepare(root,output):
    protocol=root/'configs/trajectory_guidance_protocol.json';spec=json.loads(protocol.read_text())
    run=root/'runs'/spec['parent_generation'];mp=run/'manifest.json';m=json.loads(mp.read_text());pc=m['config']
    panel=root/'runs/retrieved_context_full_20261009.json';rows=json.loads(panel.read_text())['selected']
    selected=[next(r for r in rows if r['bucket']==b) for b in (128,256,384,512)]
    c=dict(spec=spec,selected=selected,sources=[])
    paths=dict(protocol=protocol,parent_manifest=mp,parent_report=root/'reports'/(run.name+'.json'),parent_predictions=run/'predictions.h5',selection=panel,
        checkpoint=Path(pc['checkpoint']),decoder_checkpoint=Path(pc['decoder_checkpoint']),fragments=Path(pc['fragments']))
    for key,p in paths.items():
        c[key]=str(p.resolve());c['sources'].append(dict(path=str(p.resolve()),sha256=sha(p)))
    sidecar=Path(pc['checkpoint']+'.meta.json')
    if sidecar.exists():c['sources'].append(dict(path=str(sidecar.resolve()),sha256=sha(sidecar)))
    for p in [root/'src/latentfold/trajectory_guidance.py',root/'src/latentfold/decoder.py']:
        c['sources'].append(dict(path=str(p.resolve()),sha256=sha(p)))
    c['file_identity']=[identity(r['path']) for r in c['sources']]
    c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
    audit(c);output.write_text(json.dumps(c,indent=2)+'\n')


def audit(c):
    audit_worker(c);verifier=VerifiedSources()
    for r in c['sources']:verifier.verify(r)
    m=json.loads(Path(c['parent_manifest']).read_text());d=json.loads(Path(c['parent_report']).read_text())
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(c['parent_manifest']) or m['predictions_sha256']!=sha(c['parent_predictions']):raise ValueError('Unqualified original generation')
    if json.loads(Path(c['protocol']).read_text())!=c['spec']:raise ValueError('Changed protocol')
    rows=json.loads(Path(c['selection']).read_text())['selected'];expected=[next(r for r in rows if r['bucket']==b) for b in (128,256,384,512)]
    if expected!=c['selected'] or any(c[k]!=m['config'][k] for k in ('checkpoint','decoder_checkpoint','fragments')):raise ValueError('Changed paired source')


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];audit(c)
    if m['status']!='complete' or sha(run/'predictions.h5')!=m['predictions_sha256'] or m['weights_before']!=m['weights_after']:raise ValueError('Incomplete or mutated run')
    ids=[r['id'] for r in c['selected']]
    if len(m['controls'])!=len(ids) or {r['target_id'] for r in m['controls']}!=set(ids):raise ValueError('Missing controls')
    for r in m['controls']:
        if r['zero_max_abs']!=0 or r['historical_latent_max_abs']>1e-5 or r['historical_max_ca_rmsd']>.2 or r['historical_min_lddt']<.99 or not r['same_decisions']:raise ValueError('Historical parity failed')
        if r['ad_loss_error']>.001 or r['pose_gradient_relative_error']>1e-4 or not r['finite_difference_passed']:raise ValueError('Derivative control failed')
    records=[];update_error=0.
    with h5py.File(run/'predictions.h5',locking=False) as f,h5py.File(c['fragments'],locking=False) as fragments:
        for row in c['selected']:
            ident=row['id'];q=fragments['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
            for arm in ('baseline','guided'):
                g=f[arm+'/'+ident];bb=g['backbone'][:]
                if bb.shape!=(4,row['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Missing finite outputs')
                records+=raw_rows(bb,q['fragment'][:],st,arm,ident,row['family'])
                states=g['states'];prior=None
                if set(states)!=set(map(str,range(50))):raise ValueError('Missing steps')
                for i in range(50):
                    s=states[str(i)];x=s['x'][:];v=s['v'][:];direction=s['direction'][:];following=s['next'][:];t=s.attrs['t'];dt=s.attrs['dt'];w=s.attrs['weight']
                    if abs(t-i/50)>1e-7 or abs(dt-.02)>1e-7 or not all(np.isfinite(a).all() for a in (x,v,direction,following)):raise ValueError('Invalid finite integration state')
                    if i==0 and not np.array_equal(x,f['baseline/'+ident+'/states/0/x'][:]):raise ValueError('Initial noise changed')
                    wanted=.5*(1-t)/t if arm=='guided' and 25<=i<45 else 0.
                    if abs(w-wanted)>1e-7 or (prior is not None and not np.array_equal(prior,x)):raise ValueError('Changed guidance schedule/trajectory')
                    error=float(np.max(abs(following-(x+np.float32(dt)*(v-np.float32(w)*direction)))))
                    update_error=max(update_error,error)
                    if error>1e-5:raise ValueError('Euler update mismatch')
                    rms=np.sqrt(np.mean(direction**2,axis=(1,2)))
                    if wanted and not np.allclose(rms,1,atol=1e-5):raise ValueError('Missing normalized gradient')
                    if not wanted and np.any(direction):raise ValueError('Unexpected correction')
                    prior=following
                centered=prior-prior.mean(-1,keepdims=True);z=centered/np.sqrt(np.mean(centered**2,axis=-1,keepdims=True)+1e-5)
                if np.max(abs(z-g['latent'][:]))>1e-5:raise ValueError('Final latent changed')
    summary={}
    for arm in ('baseline','guided'):
        rr=[r for r in records if r['arm']==arm];summary[arm]=dict(samples=len(rr),valid=sum(r['coarse_valid'] for r in rr),raw=sum(r['raw_gate_passed'] for r in rr),raw_families=len({r['family'] for r in rr if r['raw_gate_passed']}),mean_motif_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])))
    s=summary['guided'];gate=c['spec']['gate'];qualified=s['valid']>=gate['minimum_valid'] and s['raw']>=gate['minimum_raw'] and s['raw_families']>=gate['minimum_raw_families']
    return dict(status='complete',qualified=qualified,designability_tested=False,summary=summary,records=records,controls=m['controls'],update_max_abs=update_error,batches=m['batches'],elapsed_seconds=m['elapsed_seconds'],manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'])
