"""Describe input-distribution changes without scoring or selecting model outputs."""
import argparse
from collections import Counter
import json
from pathlib import Path

import h5py
import numpy as np
from prepare_overfit import sha


def entropy(sequence):
    probabilities=np.array(list(Counter(sequence).values()),dtype=float)/len(sequence)
    return float(-(probabilities*np.log2(probabilities)).sum())


def geometry(ca):
    if ca.shape!=(20,3) or not np.isfinite(ca).all():raise ValueError('Finite20-residue backbone required')
    distance=np.linalg.norm(ca[:,None]-ca[None,:],axis=-1)
    return distance[np.triu_indices(20,1)],dict(
        radius_of_gyration=float(np.sqrt(np.square(ca-ca.mean(0)).sum(-1).mean())),
        mean_ca_distance_i3=float(np.diag(distance,3).mean()),
        mean_ca_distance_i4=float(np.diag(distance,4).mean()))


def distance_summary(features):
    x=np.asarray(features,dtype=np.float64);centered=x-x.mean(0)
    covariance=centered.T@centered/len(x)
    values=np.maximum(np.linalg.eigvalsh(covariance),0)
    return dict(mean_pair_distance_std=float(np.sqrt(np.trace(covariance)/x.shape[1])),
                distance_feature_effective_rank=float(values.sum()**2/np.square(values).sum()) if values.sum()>0 else 0.)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];source=root/'reports/fragment_quality_selection_20261003.json'
    selection=json.loads(source.read_text());protocol=Path(selection['protocol'])
    if selection['status']!='complete' or not selection['qualified'] or sha(protocol)!=selection['protocol_sha256']:raise ValueError('Unqualified selection')
    corpus=root/json.loads(protocol.read_text())['corpus'];quality=json.loads(Path(selection['quality_report']).read_text())
    if sha(corpus)!=quality['sources'][str(corpus)]:raise ValueError('Changed corpus')
    records=[];features={arm:[] for arm in ('control','quality')};sequences={arm:[] for arm in features}
    with h5py.File(corpus) as f:
        for index,r in enumerate(selection['entries']):
            g=f['train/'+r['id']]
            for arm in features:
                q=g['conditions/'+r[arm]];bb=q['fragment'][:];seq=q.attrs['sequence']
                vector,metrics=geometry(bb[:,1]);features[arm].append(vector);sequences[arm].append(seq)
                records.append(dict(arm=arm,id=r['id'],bucket=r['bucket'],condition=r[arm],
                                    sequence_entropy=entropy(seq),**metrics))
            if (index+1)%2000==0:print('audited',index+1,flush=True)
    summary=[]
    for arm in features:
        for bucket in (None,128,256,384,512):
            rows=[r for r in records if r['arm']==arm and (bucket is None or r['bucket']==bucket)]
            indices=[k for k,r in enumerate(selection['entries']) if bucket is None or r['bucket']==bucket]
            seqs=[sequences[arm][k] for k in indices]
            metrics={key:dict(median=float(np.median([r[key] for r in rows])),q10=float(np.quantile([r[key] for r in rows],.1)),q90=float(np.quantile([r[key] for r in rows],.9)))
                     for key in ('sequence_entropy','radius_of_gyration','mean_ca_distance_i3','mean_ca_distance_i4')}
            summary.append(dict(arm=arm,bucket=bucket,conditions=len(rows),unique_sequences=len(set(seqs)),
                                **distance_summary([features[arm][k] for k in indices]),metrics=metrics))
    d=dict(status='complete',sources={str(source):sha(source),str(corpus):sha(corpus)},summary=summary,records=records,
           scope='Training-input descriptive audit only. No model outputs or refold outcomes used. Sequence entropy, radius and190pair-distance features describe input diversity; they do not establish designability, secondary structure or generated-ensemble coverage. Neither condition selection nor scientific gates are changed.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Fragment-quality input diversity','',d['scope'],'',
           '|Arm|Bucket|Conditions|Unique sequences|Distance-feature rank|Pair-distance std|Median sequence entropy|Median Rg|',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        lines.append(f"|{r['arm']}|{r['bucket']}|{r['conditions']}|{r['unique_sequences']}|{r['distance_feature_effective_rank']:.2f}|{r['mean_pair_distance_std']:.2f}|{r['metrics']['sequence_entropy']['median']:.2f}|{r['metrics']['radius_of_gyration']['median']:.2f}|")
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps([r for r in summary if r['bucket'] is None]))


if __name__=='__main__':main()
