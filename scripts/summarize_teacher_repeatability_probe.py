"""Preserve all numerical replay outcomes, including strict-gate failures."""
import argparse
import itertools
import json
import math
from pathlib import Path
from prepare_overfit import sha


def analyze(m):
    if m['status'] != 'complete':
        return dict(status='failed', error=m.get('error', 'incomplete'))
    if m['design_attempts'] != 0 or [r['index'] for r in m['records']] != list(range(6)):
        raise ValueError('Wrong replay inventory')
    pairs=[(r['left'],r['right']) for r in m['comparisons']]
    if pairs != list(itertools.combinations(range(6),2)):
        raise ValueError('Missing or duplicated comparisons')
    metrics=m['comparisons']+[r['original_comparison'] for r in m['records']]
    if any(not math.isfinite(r[k]) for r in metrics for k in ('ca_rmsd','ca_lddt')):
        raise ValueError('Nonfinite comparison')
    return dict(status='complete', original_gate=dict(ca_rmsd_max=.01,ca_lddt_min=.999),
                feature_mutations=[r['index'] for r in m['records'] if r['features_before']!=r['features_after']],
                feature_rng_changes=[r['index'] for r in m['records'] if r['rng_before_features']!=r['rng_after_features']],
                fresh_feature_hashes_match=all(r['features_before']==m['records'][0]['features_before'] for r in m['records']),
                max_pair_ca_rmsd=max(r['ca_rmsd'] for r in m['comparisons']),
                failed_pairs=[r for r in m['comparisons'] if r['ca_rmsd']>.01 or r['ca_lddt']<.999],
                comparisons=m['comparisons'], original_comparisons=[r['original_comparison'] for r in m['records']],
                strict_probe=m['strict_probe'], scope=m['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1:raise ValueError('One diagnostic run required')
    path=a.runs[0]/'manifest.json';d=analyze(json.loads(path.read_text()));d['manifest_sha256']=sha(path)
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Teacher numerical replay\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')
    print(json.dumps(d))


if __name__=='__main__':main()
