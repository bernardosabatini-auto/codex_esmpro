"""Report prespecified length/continuity strata for a frozen sample selector."""
import argparse
import json
from pathlib import Path

import numpy as np
from analyze_consensus import digest
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--clusters',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();choice=json.loads(args.selection.read_text());run=Path(choice['run'])
    manifest=json.loads((run/'manifest.json').read_text());scores=json.loads((run/'scores.json').read_text())
    validate_scores(manifest,scores)
    if digest(run/'manifest.json')!=choice['manifest_sha256'] or digest(run/'predictions.h5')!=choice['predictions_sha256']:
        raise ValueError('selection inputs changed')
    clusters=json.loads(args.clusters.read_text())['clusters'];rows={}
    for row in scores['records']:
        if row['setting']==choice['setting']:rows.setdefault(row['target_id'],{})[row['sample']]=row
    if set(rows)!=set(choice['choices']) or set(rows)!=set(clusters):raise ValueError('coverage differs')
    strata={f'length_{lo+1}_{hi}':[n for n,r in rows.items() if lo<r[0]['length']<=hi]
            for lo,hi in [(0,128),(128,256),(256,384),(384,512)]}
    for broken in (False,True):
        strata['reference_CA_breaks' if broken else 'reference_CA_continuous']=[n for n,r in rows.items()
            if (r[0]['reference_adjacent_short_count']<r[0]['length']-1)==broken]
    result=dict(status='complete',diagnostic_only=True,selection_sha256=digest(args.selection),strata={})
    lines=['# Sample selection by existing development strata','',
        'Exploratory secondary analysis; no multiplicity correction. Same fixed length bins and reference-CA continuity proxy as the prior training diagnostics. These strata do not change the selector or the promotion gate. The selected structure is compared with the mean across the same three samples.','',
        '| Stratum | Targets | Mean TM | Selected TM | Change [95% cluster CI] |','|---|---:|---:|---:|---|']
    for label,names in strata.items():
        if not names:continue
        values={metric:paired_comparison(
            {n:float(np.mean([r[metric] for r in rows[n].values()])) for n in names},
            {n:rows[n][choice['choices'][n]['sample']][metric] for n in names},clusters={n:clusters[n] for n in names})
            for metric in ('tm_fixed_reference','ca_lddt')}
        result['strata'][label]=values;tm=values['tm_fixed_reference']
        lines.append(f"| {label} | {tm['n']} | {tm['ours']:.5f} | {tm['theirs']:.5f} | {tm['theirs_minus_ours']:+.5f} {tm['ci95']} |")
    args.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':main()
