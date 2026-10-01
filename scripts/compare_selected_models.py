"""Compare two frozen selectors on matching prediction and scoring protocols."""
import argparse
import json
from pathlib import Path

from analyze_consensus import digest
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores
from summarize_pilot import geometry_by_target


def read_selection(path):
    choice=json.loads(path.read_text());run=Path(choice['run'])
    if digest(run/'manifest.json')!=choice['manifest_sha256'] or digest(run/'predictions.h5')!=choice['predictions_sha256']:
        raise ValueError('frozen prediction inputs changed')
    manifest=json.loads((run/'manifest.json').read_text());scores=json.loads((run/'scores.json').read_text());validate_scores(manifest,scores)
    records=[r for r in scores['records'] if r['setting']==choice['setting'] and r['sample']==choice['choices'][r['target_id']]['sample']]
    if len(records)!=len(choice['choices']) or len({r['target_id'] for r in records})!=len(records):
        raise ValueError('selected coverage mismatch')
    return choice,manifest,scores,records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--clusters',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    first,second=map(read_selection,(a.reference,a.candidate))
    for key in ('dataset','decoder_checkpoint','precision'):
        if first[1][key]!=second[1][key]:raise ValueError('changed '+key)
    for key in ('seed','samples','target_ids','target_manifest_sha256','decoder_steps'):
        if first[1]['config'][key]!=second[1]['config'][key]:raise ValueError('changed '+key)
    if first[2]['usalign']!=second[2]['usalign'] or first[0]['setting']!=second[0]['setting'] or first[0]['policy']!=second[0]['policy']:
        raise ValueError('scoring, sampling or selection policy differs')
    clusters=json.loads(a.clusters.read_text())['clusters']
    paired={metric:paired_comparison(
        {r['target_id']:r[metric] for r in first[3]}, {r['target_id']:r[metric] for r in second[3]},clusters=clusters)
        for metric in ('tm_fixed_reference','ca_lddt')}
    geometry={key:paired_comparison(geometry_by_target(first[3],key),geometry_by_target(second[3],key),clusters=clusters)
        for key in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
    noninferior=all(paired[key]['ci95'][0]>-.005 for key in paired) and all(row['ci95'][1]<=.001 for row in geometry.values())
    result=dict(status='complete',reference_selection_sha256=digest(a.reference),candidate_selection_sha256=digest(a.candidate),
        paired=paired,geometry=geometry,development_noninferiority=noninferior,
        note='Deployment comparison of separately trained checkpoints. Not a causal architecture ablation. No matched end-to-end throughput claim.')
    lines=['# Selected pair-free versus selected pair model','',result['note'],'',
        '| Metric | Pair | Pair-free | Pair-free minus pair [95% cluster CI] |','|---|---:|---:|---|']
    for key,row in paired.items():lines.append(f"| {key} | {row['ours']:.5f} | {row['theirs']:.5f} | {row['theirs_minus_ours']:+.5f} {row['ci95']} |")
    lines+=['',f'Development noninferiority against the selected pair model: {noninferior}.', '', '```json', json.dumps(result,indent=2), '```']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines[:9]))


if __name__=='__main__':main()
