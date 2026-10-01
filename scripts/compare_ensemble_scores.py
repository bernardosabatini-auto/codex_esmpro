"""Paired family comparisons on the same frozen 48-protein development panel."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np


def compare(candidate, reference, families):
    ids=sorted(candidate)
    if not ids or set(ids)!=set(reference) or len({families[i] for i in ids})!=len(ids):raise ValueError('expected paired unique families')
    a=np.array([candidate[i] for i in ids]);b=np.array([reference[i] for i in ids]);delta=a-b
    if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('nonfinite score')
    boot=np.random.default_rng(20261001).choice(delta,(10000,len(delta)),replace=True).mean(1)
    return dict(families=len(ids),candidate=float(a.mean()),reference=float(b.mean()),candidate_minus_reference=float(delta.mean()),ci95=np.quantile(boot,[.025,.975]).tolist(),positive_differences=int((delta>0).sum()),negative_differences=int((delta<0).sum()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate-setting',default='cfg2/latent');p.add_argument('--reference-setting',default='cfg2/latent');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    ca,ref=(json.loads(path.read_text()) for path in (a.candidate,a.reference))
    if ca['status']!='complete' or ref['status']!='complete' or ca['protocol_sha256']!=ref['protocol_sha256'] or ca['definitions']!=ref['definitions']:raise ValueError('incomplete or mismatched reference protocol')
    x={r['target_id']:r for r in ca['rows'] if r['setting']==a.candidate_setting};y={r['target_id']:r for r in ref['rows'] if r['setting']==a.reference_setting}
    if set(x)!=set(y) or len(x)!=48:raise ValueError('exact same 48 development targets required')
    families={k:r['family'] for k,r in x.items()}
    if any(x[k]['family']!=y[k]['family'] or x[k]['category']!=y[k]['category'] for k in x):raise ValueError('family/category mismatch')
    getters={'coverage_at_32':lambda r:r['coverage']['2.0']['32'],'ca_lddt':lambda r:r['oracle_nearest_reference_ca_lddt_mean'],'coarse_valid':lambda r:r['coarse_valid_fraction'],'md_w1':lambda r:r['projection_wasserstein']['32']};metrics={}
    for name,getter in getters.items():
        left={};right={}
        for ident in x:
            try:l=getter(x[ident]);r=getter(y[ident])
            except KeyError:continue
            left[ident]=l;right[ident]=r
        metrics[name]=compare(left,right,families)
    quality=metrics['ca_lddt']['ci95'][0]>-.005;validity=metrics['coarse_valid']['candidate_minus_reference']>=-.01;coverage=metrics['coverage_at_32']
    d=dict(status='complete',candidate=str(a.candidate.resolve()),candidate_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),reference=str(a.reference.resolve()),reference_sha256=hashlib.sha256(a.reference.read_bytes()).hexdigest(),candidate_setting=a.candidate_setting,reference_setting=a.reference_setting,metrics=metrics,sampling_quality_gate_passed=bool(quality and validity and coverage['candidate_minus_reference']>=0),training_diversity_gate_passed=bool(quality and validity and coverage['candidate_minus_reference']>=.1 and coverage['ci95'][0]>0))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Paired ensemble development comparison','',f'Candidate: {a.candidate.parent.name}/{a.candidate.name}, {a.candidate_setting}. Reference: {a.reference.parent.name}/{a.reference.name}, {a.reference_setting}.','', '| Metric | Families | Candidate | Reference | Difference | 95% family interval |','|---|---:|---:|---:|---:|---|']
    for name,r in metrics.items():lines.append(f"| {name} | {r['families']} | {r['candidate']:.5f} | {r['reference']:.5f} | {r['candidate_minus_reference']:+.5f} | [{r['ci95'][0]:+.5f}, {r['ci95'][1]:+.5f}] |")
    lines+=['',f"Sampling quality gate: {d['sampling_quality_gate_passed']}. Training diversity gate: {d['training_diversity_gate_passed']}.",'','MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
