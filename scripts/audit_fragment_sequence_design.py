"""Posthoc diagnostics on the outcome-independent32-family designability panels."""
import argparse
import itertools
import json
import re
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from prepare_overfit import sha


def fasta_scores(path, length, motif_length):
    lines=path.read_text().splitlines();rows=[]
    for k,line in enumerate(lines):
        if line.startswith('>T='):
            score=float(re.search(r', score=([0-9.]+)',line).group(1))
            global_score=float(re.search(r', global_score=([0-9.]+)',line).group(1))
            sequence=lines[k+1]
            if len(sequence)!=length:raise ValueError('Incomplete MPNN sequence')
            rows.append(dict(sequence=sequence,scaffold_nll=score,global_nll=global_score,
                             motif_nll=(global_score*length-score*(length-motif_length))/motif_length))
    if len(rows)!=8:raise ValueError('Expected eight fixed-budget designs')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1];records=[];sources={}
    for task in ('c20','f30'):
        comparison=root/f'reports/broad_fragment_{task}_center_comparison.json'
        report=json.loads(comparison.read_text());panel=set(report['fixed_panel_designability']['target_ids'])
        sources[str(comparison)]=sha(comparison)
        for source in report['source_reports']:
            path=Path(source['path']);d=json.loads(path.read_text())
            if sha(path)!=source['sha256']:raise ValueError('Changed refold summary')
            run=root/'runs'/path.stem;manifest=json.loads((run/'manifest.json').read_text())
            if sha(run/'manifest.json')!=d['manifest_sha256']:raise ValueError('Changed sequence manifest')
            for r in d['records']:
                if r['target_id'] not in panel or r['generation_slot']!=0 or r['arm']=='native':continue
                fasta=run/'mpnn/seqs'/(r['name']+'.fa');scores=fasta_scores(fasta,r['length'],len(r['fixed_sequence']))
                if [q['sequence'] for q in scores]!=manifest['sequences'][r['name']]:raise ValueError('Changed designed sequences')
                mask=np.ones(r['length'],bool);mask[r['fixed_start']:r['fixed_start']+len(r['fixed_sequence'])]=False
                identities=[float((np.array(list(a['sequence']))[mask]==np.array(list(b['sequence']))[mask]).mean()) for a,b in itertools.combinations(scores,2)]
                records.append(dict(task=task,arm=r['arm'],target_id=r['target_id'],family=r['family'],length=r['length'],
                                    designable=r['valid_designable'],strong_joint=r['scaffold_joint_success'],
                                    scaffold_nll=float(np.mean([q['scaffold_nll'] for q in scores])),
                                    motif_nll=float(np.mean([q['motif_nll'] for q in scores])),
                                    unique_sequences=len({q['sequence'] for q in scores}),
                                    mean_scaffold_sequence_identity=float(np.mean(identities)),
                                    best_valid_tm=max([q['sc_tm'] for q in r['refolds'] if q['coarse_valid']] or [0.]),
                                    designable_by_budget={str(k):bool(r['raw']['coarse_valid'] and any(q['coarse_valid'] and q['sc_tm']>.5 for q in r['refolds'][:k])) for k in (1,2,4,8)},
                                    fasta_sha256=sha(fasta)))
    if len(records)!=256 or len({(r['task'],r['arm'],r['target_id']) for r in records})!=256:
        raise ValueError('Changed fixed panel denominator')
    summary=[]
    for task,arm in sorted({(r['task'],r['arm']) for r in records}):
        rows=[r for r in records if (r['task'],r['arm'])==(task,arm)]
        summary.append(dict(task=task,arm=arm,n=len(rows),
                            median_unique_sequences=float(np.median([r['unique_sequences'] for r in rows])),
                            median_scaffold_identity=float(np.median([r['mean_scaffold_sequence_identity'] for r in rows])),
                            median_scaffold_nll=float(np.median([r['scaffold_nll'] for r in rows])),
                            median_motif_nll=float(np.median([r['motif_nll'] for r in rows])),
                            scaffold_nll_best_tm_spearman=float(spearmanr([r['scaffold_nll'] for r in rows],[r['best_valid_tm'] for r in rows]).statistic),
                            motif_nll_best_tm_spearman=float(spearmanr([r['motif_nll'] for r in rows],[r['best_valid_tm'] for r in rows]).statistic),
                            designable_by_budget={str(k):sum(r['designable_by_budget'][str(k)] for r in rows) for k in (1,2,4,8)}))
    result=dict(status='complete',sources=sources,summary=summary,records=records,
                scope='Exploratory failure diagnosis, not a validated selection policy or training labels.32shared families/arm/task; samples are dependent. Motif NLL is reconstructed from four-decimal whole-chain and redesigned-region scores. Correlations are descriptive, with no significance claim.')
    args.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Fragment sequence-design diagnosis','',result['scope'],'',
           '|Task|Arm|Median unique /8|Scaffold sequence identity|Scaffold NLL|Motif NLL|Designable at1/2/4/8 attempts /32|',
           '|---|---|---:|---:|---:|---:|---|']
    for r in summary:
        curve='/'.join(str(r['designable_by_budget'][str(k)]) for k in (1,2,4,8))
        lines.append(f"|{r['task']}|{r['arm']}|{r['median_unique_sequences']:.0f}|{r['median_scaffold_identity']:.3f}|{r['median_scaffold_nll']:.3f}|{r['median_motif_nll']:.3f}|{curve}|")
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
