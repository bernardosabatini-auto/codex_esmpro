"""Choose better-supported training fragments with matched protein/position counts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from prepare_overfit import sha


def assign(qualities, identifiers, conditions, seed):
    quality=np.asarray(qualities,dtype=np.float64)
    if quality.shape!=(len(identifiers),len(conditions)) or len(set(identifiers))!=len(identifiers) or not len(identifiers):
        raise ValueError('Invalid assignment inventory')
    if not np.isfinite(quality).all() or (quality<0).any() or (quality>100).any():raise ValueError('Invalid confidence')
    order=sorted(range(len(identifiers)),key=lambda i:hashlib.sha256(f'{seed}:{identifiers[i]}'.encode()).hexdigest())
    baseline=np.empty(len(identifiers),dtype=np.int64)
    for k,i in enumerate(order):baseline[i]=k%len(conditions)
    slots=np.sort(baseline)
    rows,columns=linear_sum_assignment(-quality[:,slots])
    candidate=np.empty_like(baseline);candidate[rows]=slots[columns]
    if Counter(baseline)!=Counter(candidate):raise ValueError('Changed placement counts')
    old=quality[np.arange(len(identifiers)),baseline];new=quality[np.arange(len(identifiers)),candidate]
    if new.sum()+1e-8<old.sum():raise ValueError('Assignment worse than feasible baseline')
    return baseline,candidate,old,new


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_condition_quality_selection_protocol.json'
    spec=json.loads(protocol.read_text());source=root/spec['quality_report'];report=json.loads(source.read_text())
    if report['status']!='complete':raise ValueError('Incomplete quality audit')
    for path,digest in report['sources'].items():
        if sha(path)!=digest:raise ValueError('Changed quality provenance')
    names=spec['conditions'];index={}
    for r in report['records']:
        if r['condition'] not in names:continue
        index.setdefault(r['id'],{})[r['condition']]=r
    if len(index)!=spec['proteins'] or any(set(rs)!=set(names) for rs in index.values()):raise ValueError('Incomplete20-residue inventory')
    entries=[];summary=[]
    for bucket in (128,256,384,512):
        ids=sorted(i for i,rs in index.items() if rs[names[0]]['bucket']==bucket)
        q=np.asarray([[index[i][name]['mean_plddt'] for name in names] for i in ids])
        before,after,old,new=assign(q,ids,names,spec['seed'])
        for k,ident in enumerate(ids):
            if any(index[ident][name]['motif_length']!=20 for name in names):raise ValueError('Changed motif length')
            entries.append(dict(id=ident,bucket=bucket,control=names[before[k]],quality=names[after[k]],
                                control_confidence=float(old[k]),quality_confidence=float(new[k])))
        summary.append(dict(bucket=bucket,proteins=len(ids),control_mean=float(old.mean()),quality_mean=float(new.mean()),
                            gain=float((new-old).mean()),changed_conditions=int((before!=after).sum()),
                            placement_counts={names[k]:int((before==k).sum()) for k in range(3)}))
    gain=float(np.mean([r['quality_confidence']-r['control_confidence'] for r in entries]))
    qualified=gain>=spec['minimum_overall_confidence_gain'] and all(r['gain']>=spec['minimum_bucket_confidence_gain'] for r in summary)
    result=dict(status='complete',qualified=qualified,protocol=str(protocol),protocol_sha256=sha(protocol),
                quality_report=str(source),quality_report_sha256=sha(source),overall_gain=gain,summary=summary,entries=entries,
                scope=spec['scope'])
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Matched fragment-quality selection','',spec['scope'],'',f'Feasibility qualified: {qualified}. Mean confidence gain: {gain:.3f}.','',
           '|Length bucket|Proteins|Control mean|Quality mean|Gain|Changed conditions|', '|---|---:|---:|---:|---:|---:|']
    lines += [f"|{r['bucket']}|{r['proteins']}|{r['control_mean']:.2f}|{r['quality_mean']:.2f}|{r['gain']:.2f}|{r['changed_conditions']}|" for r in summary]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('entries','scope')}))


if __name__=='__main__':main()
