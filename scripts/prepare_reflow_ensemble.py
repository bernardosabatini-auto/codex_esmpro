"""Freeze a predeclared short-sampler checkpoint for the ensemble panel."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np


def digest(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--sampling-steps',type=int,choices=(5,10),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.run/'manifest.json';m=json.loads(path.read_text());c=m['config']
    if c['arm'] not in ('reflow_paired','reflow_independent'):raise ValueError('unexpected sampler arm')
    if m['status'] not in ('running','complete') or m['updates']<a.step or c.get('profile_only'):raise ValueError('checkpoint not eligible')
    selection=json.loads(Path(c['selection']).read_text());expected={r['id'] for r in selection['tuning']}
    if digest(c['selection'])!=c['selection_sha256'] or len(expected)!=64:raise ValueError('changed tuning selection')
    means={}
    for step in (0,a.step):
        rows=[r for r in m['scores'] if r['step']==step and r['sampling_steps']==(25 if step==0 else a.sampling_steps)]
        if len(rows)!=192 or {r['target_id'] for r in rows}!=expected or any({r['sample'] for r in rows if r['target_id']==i}!={0,1,2} for i in expected):raise ValueError('checkpoint tuning evaluation not finished')
        means[step]=float(np.mean([r['ca_lddt'] for r in rows]))
    checkpoint=a.run/f'ema_{a.step}.ckpt';snapshot=Path('runs/ensemble_training_snapshots')/f'{a.run.name}_step{a.step}.json';snapshot.parent.mkdir(exist_ok=True)
    # The live training manifest keeps changing; snapshot the completed endpoint.
    if not snapshot.exists():snapshot.write_text(json.dumps(m,indent=2)+'\n')
    config=json.loads(Path('runs/ensemble_49618816/manifest.json').read_text())['config'];cache=Path('runs/ensemble_49618816/embeddings.h5').resolve()
    config.update(checkpoint=str(checkpoint.resolve()),checkpoint_sha256=digest(checkpoint),embedding_cache=str(cache),embedding_cache_sha256=digest(cache),training_manifest=str(snapshot.resolve()),training_manifest_sha256=digest(snapshot),checkpoint_selection=dict(rule='Both predeclared500/2000 endpoints get ensemble development evaluation; no confirmation/test selection',selected_step=a.step,mean_ca_lddt=means,arm=c['arm']),flow_steps=a.sampling_steps,primary_guidance=1,guidance_controls=[],work_cap_seconds=1500)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(config,indent=2)+'\n');print(json.dumps(config['checkpoint_selection']))


if __name__=='__main__':main()
