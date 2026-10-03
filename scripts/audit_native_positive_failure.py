"""Post hoc diagnosis of existing controls; no new samples or selection changes."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from extra_fragment_validation_core import load_conditions
from fragment_validation_core import raw_rows
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    comparison=root/'reports/native_positive_model_comparison_20261003.json';result=json.loads(comparison.read_text())
    if result['status']!='complete' or result['development_screen_qualified']!={'positive_coverage':False}:raise ValueError('This diagnosis is bound to the completed failed coverage experiment')
    run=root/'runs/native_anchor_training_50253917';mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];report=root/'reports'/(run.name+'.json');d=json.loads(report.read_text())
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or m['updates']!=400:raise ValueError('Incomplete or changed training run')
    lp=Path(c['labels_manifest']);labels=json.loads(lp.read_text());sources=[]
    def bind(path):sources.append(dict(path=str(path),sha256=sha(path)))
    for path in (comparison,mp,report,lp,Path(labels['positives']),Path(c['fragments'])):bind(path)
    if sha(labels['positives'])!=labels['positives_sha256']:raise ValueError('Changed label arrays')
    items=load_conditions(c['fragments'],c['control_ids'],'c20_center',cohort='train');training=set(c['training_ids']);rows=[]
    for step in (0,400):
        ep=run/f'evaluation_{step}.h5';bind(ep);scored=[]
        with h5py.File(ep) as f:
            for ident,item in items.items():
                for mode in ('conditioned','null'):
                    bb=f[mode+'/'+ident+'/backbone'][:]
                    if bb.shape!=(4,item['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Invalid stored controls')
                    rr=raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family'])
                    if mode=='conditioned':scored.extend(rr)
                    rows += [dict(r,step=step,mode=mode,in_training=ident in training) for r in rr]
        if scored!=next(e['records'] for e in m['evaluations'] if e['step']==step):raise ValueError('Stored control scores changed')
    summary=[]
    for step in (0,400):
        for mode in ('conditioned','null'):
            rr=[r for r in rows if r['step']==step and r['mode']==mode and r['in_training']]
            summary.append(dict(step=step,mode=mode,proteins=len({r['target_id'] for r in rr}),samples=len(rr),raw=sum(r['raw_gate_passed'] for r in rr),
                                mean_motif_ca_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])),mean_motif_drms=float(np.mean([r['motif_drms'] for r in rr]))))
    projection=[]
    with h5py.File(labels['positives']) as f:
        for r in labels['rows']:
            z=torch.from_numpy(f[r['target_id']+'/positive'][:]);delta=torch.nn.functional.layer_norm(z,(8,))-z
            projection.append(dict(target_id=r['target_id'],maximum_absolute_change=float(delta.abs().max()),rms_change=float(delta.square().mean().sqrt())))
    out=dict(status='complete',source_reports=sources,controls=summary,records=rows,projection=projection,
             maximum_native_projection_change=max(r['maximum_absolute_change'] for r in projection),
             scope='Post hoc numerical/mechanistic audit of three previously chosen historical controls that are also qualified training positives. No new target selection, samples, refolds, checkpoint choices, or generalization claim. Conditioning versus null measures responsiveness; raw geometry alone does not establish designability. Native projection audit measures latent changes only, not decoded coordinate equivalence.')
    a.output.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=['# Coverage failure: existing-control diagnosis','',out['scope'],'','|Step|Condition|Training proteins|Samples|Raw successes|Mean motif CA RMSD|Mean motif dRMS|','|---|---|---:|---:|---:|---:|---:|']
    for r in summary:lines.append(f"|{r['step']}|{r['mode']}|{r['proteins']}|{r['samples']}|{r['raw']}|{r['mean_motif_ca_rmsd']:.3f}|{r['mean_motif_drms']:.3f}|")
    lines += ['',f"Across all 52 qualified endpoint latents, terminal normalization changes any component by at most {out['maximum_native_projection_change']:.8g}. This excludes a large normalization mismatch in the reference endpoints; it does not test every sampler failure mechanism."]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
