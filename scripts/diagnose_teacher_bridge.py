"""Oracle Gaussian-bridge posterior for a frozen, audited teacher label panel."""
import argparse,json
from pathlib import Path
import numpy as np,h5py
from latentfold.teacher_states import bridge_posterior
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--labels',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.labels.read_text());labels=a.labels.parent/'labels.h5'
    if m['status']!='complete' or sha(labels)!=m['labels_sha256']:raise ValueError('label provenance mismatch')
    rows=[];times=(0.,.01,.025,.05,.1,.25,.5,.75,.9,.95,.99)
    with h5py.File(labels) as h:
        for index,r in enumerate(m['config']['targets']):
            g=h[r['id']];state=r['state_definition'];valid=state['teacher_indices'];chosen=np.tile(np.arange(len(valid)),16);noise=np.random.default_rng(2026100171+index).normal(size=(len(chosen),r['length']*8))
            for arm,key in [('aligned','teacher_z_aligned'),('pca','teacher_z_pca')]:
                y=g[key][:][valid].reshape(len(valid),-1)
                for t in times:rows.append(dict(target_id=r['id'],arm=arm,time=t,**bridge_posterior(y,state['clusters'],chosen,noise,t)))
    summary=[]
    for arm in ('aligned','pca'):
        for t in times:
            group=[r for r in rows if r['arm']==arm and r['time']==t];summary.append(dict(arm=arm,time=t,**{k:float(np.mean([r[k] for r in group])) for k in ('oracle_state_accuracy','true_state_posterior','state_entropy_bits','oracle_velocity_mse_floor')}))
    scope='Uniform finite teacher labels plus Gaussian bridge noise, conditional on knowing the target protein. Training-label diagnostic only; not learned accuracy, state coverage or biological populations. Both frames use identical Gaussian draws. Reported velocity MSE floor is posterior latent variance divided by (1-t)^2 per coordinate, averaged over simulated bridges.'
    a.output.with_suffix('.json').write_text(json.dumps(dict(status='complete',source=str(a.labels),source_sha256=sha(a.labels),scope=scope,rows=rows,summary=summary),indent=2)+'\n')
    lines=['# Teacher-frame Gaussian-bridge diagnostic','',scope,'','| Frame | Time | Oracle state accuracy | True-state posterior | State entropy (bits) | Velocity MSE floor |','|---|---:|---:|---:|---:|---:|']
    for r in summary:lines.append(f"| {r['arm']} | {r['time']:.3f} | {r['oracle_state_accuracy']:.5f} | {r['true_state_posterior']:.5f} | {r['state_entropy_bits']:.5f} | {r['oracle_velocity_mse_floor']:.6f} |")
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
