"""Reuse an unchanged aligned-label audit with worst-case bounds under each prior."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.audit_bounds import teacher_priors,worst_failure_mass
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--capacity-selection',type=Path,default=Path('runs/overfit_reliable_selection.json'));a=p.parse_args()
    inv=json.loads(a.inventory.read_text());audit=json.loads(a.audit.read_text());rows=inv['targets']
    if inv['status']!='complete' or audit['status']!='complete' or len(rows)!=122 or len({r['id'] for r in rows})!=122 or len({r['family'] for r in rows})!=122:raise ValueError('expected original122 eligible training families and complete audit')
    if sha(inv['selection'])!=inv['selection_sha256'] or sha(inv['protocol'])!=inv['protocol_sha256']:raise ValueError('inventory source changed')
    if audit['config']['selection_sha256']!=inv['selection_sha256']:raise ValueError('different underlying training corpus')
    capacity=json.loads(a.capacity_selection.read_text());byid={r['id']:r for r in rows}
    if len(capacity['targets'])!=32 or set(inv['capacity_ids'])!={r['id'] for r in capacity['targets']} or any(byid.get(r['id'])!=r for r in capacity['targets']):raise ValueError('original32 selection not reproduced')
    allowed={}
    for shard in audit['config']['label_shards']:
        path=Path(shard['manifest']);m=json.loads(path.read_text())
        if sha(path)!=shard['manifest_sha256'] or m['status']!='complete' or m['config']['latent_frame']!='teacher_CA_aligned_to_cached_reference':raise ValueError('incompatible aligned source')
        allowed[str((path.parent/'labels.h5').resolve())]=shard['labels_sha256']
    lookup={r['id']:r for r in audit['rows']}
    if len(lookup)!=512 or len(audit['controls'])!=4:raise ValueError('incomplete historical audit')
    if any(not r['validity_exact'] or r['max_metric_difference']>1e-3 for r in audit['controls']):raise ValueError('historical metric controls failed')
    targets=[]
    for r in rows:
        if allowed.get(r['source_labels'])!=r['source_labels_sha256']:raise ValueError('inventory labels do not match audited arrays')
        ar=lookup[r['id']];state=r['state_definition']
        if len(state['teacher_indices'])!=ar['input_valid'] or not np.isfinite(ar['min_ca_lddt']) or not 0<=ar['min_ca_lddt']<=1:raise ValueError('invalid audit counts or scores')
        priors=teacher_priors(state);failed=16-ar['decoded_valid']
        targets.append(dict(id=r['id'],bucket=r['bucket'],states=state['states'],decoded_failures=failed,ca_lddt_lower=ar['min_ca_lddt'],validity_lower={k:1-worst_failure_mass(w,failed) for k,w in priors.items()}))
    summary={}
    for bucket in (None,128,256,384,512):
        subset=[r for r in targets if bucket is None or r['bucket']==bucket]
        summary[str(bucket or 'all')]=dict(targets=len(subset),decoded_failures=sum(r['decoded_failures'] for r in subset),ca_lddt_lower=float(np.mean([r['ca_lddt_lower'] for r in subset])),validity_lower={k:float(np.mean([r['validity_lower'][k] for r in subset])) for k in ('empirical','balanced')})
    overall=summary['all'];passed=overall['ca_lddt_lower']>=.98 and all(v>=.99 for v in overall['validity_lower'].values())
    d=dict(status='complete',reconstruction_gate_passed=bool(passed),inventory=str(a.inventory.resolve()),inventory_sha256=sha(a.inventory),audit=str(a.audit.resolve()),audit_sha256=sha(a.audit),capacity_selection_sha256=sha(a.capacity_selection),summary=summary,targets=targets,scope='Conservative bounds for the existing fixed-noise aligned reconstruction audit only. This is not a fresh decoder audit, confidence interval or guarantee for all noise seeds. No student-dependent selection, new labels or training execution.')
    lines=['# Reconstruction bounds for the122-protein cohort','',d['scope'],'',
           'The metadata rule exactly reproduces the original32 selections and identifies90 additional training proteins. Every candidate refers to the same hash-bound label arrays as the completed512-protein audit. Each decoder failure is pessimistically assigned to a highest-weight valid teacher label; the per-protein minimum CA-lDDT bounds every weighted average. Invalid source labels have zero sampling weight. Average bounds weight proteins equally.','',
           '| Padded length | Proteins | Decoded failures | CA-lDDT lower bound | Empirical-prior validity lower bound | Balanced-prior validity lower bound |','|---|---:|---:|---:|---:|---:|']
    for name,r in summary.items():lines.append(f"| {name} | {r['targets']} | {r['decoded_failures']} | {r['ca_lddt_lower']:.6f} | {r['validity_lower']['empirical']:.6f} | {r['validity_lower']['balanced']:.6f} |")
    lines+=['',f'Existing reconstruction margins passed conservatively: {passed}.','',
           'These bounds permit reusing the existing aligned labels for a future matched prior experiment if the transfer decision supports expansion. They do not certify PCA labels, changed decoder weights/code, other random decoder seeds or student generalization. The122-family cohort has5/70/25/22 targets by length bucket; any broader training must account for that imbalance explicitly. No larger training run is launched by this certificate.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
