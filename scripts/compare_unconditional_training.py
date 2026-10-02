"""Compare matched unconditional paired/independent arms without selecting a seed."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from summarize_unconditional_reflow import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--paired',type=Path,required=True);p.add_argument('--independent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();runs=[a.paired,a.independent];audits=[analyze(r) for r in runs]
    if any(r['status']!='complete' or r['profile_only'] or r['updates']!=1000 for r in audits):raise ValueError('Both full arms required')
    manifests=[json.loads((r/'manifest.json').read_text()) for r in runs];pc,ic=[m['config'] for m in manifests]
    if (pc['arm'],ic['arm'])!=('paired','independent'):raise ValueError('Wrong arm order')
    ignore={'arm'}
    if {k:v for k,v in pc.items() if k not in ignore}!={k:v for k,v in ic.items() if k not in ignore}:raise ValueError('Unmatched recipes')
    for x,y in zip(manifests[0]['training'],manifests[1]['training']):
        for key in ('step','length','batch','indices','learning_rate','self_conditioned','time_sha256','rng_sha256','global_rng_sha256'):
            if x[key]!=y[key]:raise ValueError('Training schedule mismatch '+key)
    if manifests[0]['frozen_initial']!=manifests[1]['frozen_initial']:raise ValueError('Initial unused weights differ')
    # Identical initial outputs are separately checked against the same archived original10.
    comparisons=[]
    for step in (0,500,1000):
        left=next(r['scores'] for r in manifests[0]['evaluations'] if r['step']==step);right=next(r['scores'] for r in manifests[1]['evaluations'] if r['step']==step);families=sorted({r['family'] for r in left});rng=np.random.default_rng(2026100215);ix=rng.integers(0,len(families),(20000,len(families)));delta=np.array([np.mean([r['coarse_valid'] for r in left if r['family']==f])-np.mean([r['coarse_valid'] for r in right if r['family']==f]) for f in families]);comparisons.append(dict(step=step,paired_minus_independent_validity=float(delta.mean()),family_interval=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
    d=dict(status='complete',arms=audits,comparisons=comparisons,sources=[dict(path=str(r/'manifest.json'),sha256=sha(r/'manifest.json')) for r in runs]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Matched unconditional trajectory compression','','Both arms use identical labels, initial weights and every logged target/time/dropout/LR draw; independent versus recorded Gaussian coupling is the sole declared training difference. All raw generation failures retained.','', '| Arm | Step | Raw validity | Mapping CA-lDDT | Geometry screen |','|---|---:|---:|---:|---|']
    for arm in audits:
        for r in arm['summaries']:lines.append(f"| {arm['arm']} | {r['step']} | {r['coarse_valid']:.4f} | {r['ca_lddt_to_same_noise_teacher']:.4f} | {r['raw_geometry_screen_passed']} |")
    for r in comparisons:lines+=['',f"Step{r['step']} paired minus independent validity {r['paired_minus_independent_validity']:+.4f},95%family interval {r['family_interval']}."]
    lines+=['','A geometry-qualified checkpoint still requires the matched motif/ProteinMPNN assay. Mapping fidelity is descriptive; changing the correspondence between Gaussian draws and outputs can preserve a distribution. No conditional-folding, designability or new biological-state claim. No independent tests scored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
