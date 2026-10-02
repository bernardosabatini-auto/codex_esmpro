"""Development-only sequence overlap screen; never alter or filter the panel."""
import argparse,json
from pathlib import Path
import numpy as np
from Bio.Align import PairwiseAligner,substitution_matrices
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.data_manifest.read_text());c=m['config'];training=c['training_targets'];dev=c['development_rows']
    if m['status']!='complete' or len(training)!=32 or len(dev)!=16:raise ValueError('Expected current audited development corpus')
    aligner=PairwiseAligner(mode='global',substitution_matrix=substitution_matrices.load('BLOSUM62'),open_gap_score=-10,extend_gap_score=-.5);records=[]
    for d in dev:
        candidates=[]
        for t in training:
            alignment=aligner.align(d['sequence'],t['sequence'])[0];ix=alignment.indices;valid=(ix>=0).all(0);matches=sum(d['sequence'][i]==t['sequence'][j] for i,j in ix[:,valid].T);candidates.append(dict(training_id=t['id'],matches=matches,alignment_columns=ix.shape[1],aligned_pairs=int(valid.sum()),identity_over_alignment=matches/ix.shape[1],identity_over_shorter=matches/min(len(d['sequence']),len(t['sequence'])),shorter_coverage=float(valid.sum())/min(len(d['sequence']),len(t['sequence']))))
        records.append(dict(target_id=d['target_id'],closest_by_shorter=max(candidates,key=lambda x:x['identity_over_shorter']),closest_by_alignment=max(candidates,key=lambda x:x['identity_over_alignment'])))
    d=dict(status='complete',data_manifest_sha256=sha(a.data_manifest),training_sequences=32,development_sequences=16,alignments=512,method='BLOSUM62 global alignment, gap open10/extend.5; both all-column and shorter-sequence identity denominators; descriptive screen, not a homology certificate',records=records,maximum_identity_over_alignment=max(r['closest_by_alignment']['identity_over_alignment'] for r in records),maximum_identity_over_shorter=max(r['closest_by_shorter']['identity_over_shorter'] for r in records),development_above_30percent_shorter=sum(r['closest_by_shorter']['identity_over_shorter']>=.3 for r in records));a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# Fragment development sequence-overlap screen\n\nDevelopment panel only; no locked sequences or structures examined. This checks overlap with the32new fine-tuning proteins, not the inherited pretraining corpus. It does not establish novelty or replace a full homology split. No panel filtering.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(view,indent=2))

if __name__=='__main__':main()
