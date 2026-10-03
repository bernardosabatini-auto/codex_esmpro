"""Bind per-condition AFDB confidence to unchanged training fragments only."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from audit_fragment_source_confidence import read_ca
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    source=root/'reports/broad_fragment_source_confidence_20261003.json'
    d=json.loads(source.read_text())
    if d['status']!='complete' or len(d['records'])!=7941:raise ValueError('Wrong source inventory')
    corpus=root/'runs/broad_fragment_corpora_20261003/broad'
    manifest=json.loads((corpus/'manifest.json').read_text())
    sequences={r['id']:r['sequence'] for r in manifest['config']['training_targets']}
    sources={str(path):sha(path) for path in (source,corpus/'manifest.json',corpus/'fragments.h5')}
    records=[]
    with h5py.File(corpus/'fragments.h5') as f:
        if set(sequences)!=set(f['train']) or set(sequences)&set(f['development']):raise ValueError('Changed training separation')
        for k,r in enumerate(d['records']):
            path=Path(r['source_pdb'])
            if sha(path)!=r['source_sha256']:raise ValueError('Changed source PDB')
            _,confidence=read_ca(path,sequences[r['id']]);g=f['train/'+r['id']]
            for name,q in g['conditions'].items():
                start=int(q.attrs['start']);seq=q.attrs['sequence'];stop=start+len(seq)
                if start<0 or stop>len(confidence) or sequences[r['id']][start:stop]!=seq:raise ValueError('Changed fragment mapping')
                values=confidence[start:stop]
                records.append(dict(id=r['id'],cohort=r['cohort'],bucket=r['bucket'],length=r['length'],
                                    condition=name,start=start,motif_length=len(seq),mean_plddt=float(values.mean()),
                                    fraction_below70=float((values<70).mean()),source_sha256=r['source_sha256']))
            if (k+1)%1000==0:print('audited',k+1,flush=True)
    names=sorted({r['condition'] for r in records})
    if len(names)!=12 or len(records)!=7941*12 or len({(r['id'],r['condition']) for r in records})!=len(records):
        raise ValueError('Incomplete condition coverage')
    summary=[];feasibility=[]
    for cohort in ('original512','added7429'):
        rows=[r for r in records if r['cohort']==cohort]
        for name in names:
            rs=[r for r in rows if r['condition']==name]
            summary.append(dict(cohort=cohort,condition=name,conditions=len(rs),
                                median_mean_plddt=float(np.median([r['mean_plddt'] for r in rs])),
                                mean_plddt_ge90=sum(r['mean_plddt']>=90 for r in rs),
                                median_fraction_below70=float(np.median([r['fraction_below70'] for r in rs]))))
        for bucket in (128,256,384,512):
            groups={}
            for r in rows:
                if r['bucket']==bucket and r['condition'].startswith('c20_'):groups.setdefault(r['id'],[]).append(r)
            counts=[sum(r['mean_plddt']>=90 for r in rs) for rs in groups.values()]
            if any(len(rs)!=3 for rs in groups.values()):raise ValueError('Incomplete equal-length alternatives')
            feasibility.append(dict(cohort=cohort,bucket=bucket,proteins=len(groups),
                                    any_high=sum(k>0 for k in counts),all_high=sum(k==3 for k in counts),
                                    mixed_quality=sum(0<k<3 for k in counts),
                                    median_within_protein_range=float(np.median([max(r['mean_plddt'] for r in rs)-min(r['mean_plddt'] for r in rs) for rs in groups.values()]))))
    result=dict(status='complete',sources=sources,records=records,summary=summary,within_protein_feasibility=feasibility,
                scope='Training-only95,292condition audit; no model inference or refold selection. Source-context AFDB confidence is not proof of fragment stability or designability.90is a declared feasibility threshold, not an optimized outcome cutoff. Left/center/right location is a confound requiring matched counts in any future quality intervention.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Training-condition quality audit','',result['scope'],'',
           '|Cohort|Condition|N|Median mean pLDDT|Mean pLDDT >=90|',
           '|---|---|---:|---:|---:|']
    lines += [f"|{r['cohort']}|{r['condition']}|{r['conditions']}|{r['median_mean_plddt']:.2f}|{r['mean_plddt_ge90']}|" for r in summary]
    lines += ['', '|Cohort|Length bucket|Proteins|Any high|All high|Mixed quality|Median confidence range|',
              '|---|---:|---:|---:|---:|---:|---:|']
    lines += [f"|{r['cohort']}|{r['bucket']}|{r['proteins']}|{r['any_high']}|{r['all_high']}|{r['mixed_quality']}|{r['median_within_protein_range']:.2f}|" for r in feasibility]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(feasibility))


if __name__=='__main__':main()
