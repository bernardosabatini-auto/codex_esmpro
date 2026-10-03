"""Matched quality-selection intervention; condition identity differs by design."""
import argparse
import json
from pathlib import Path
from compare_broad_fragment_training import initial_parity
from fragment_quality_training import compare_quality_traces
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_quality_training_protocol.json'
    spec=json.loads(protocol.read_text());manifests={};reports={};paths={};sources=[]
    for run in a.runs:
        mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];arm=c['extension_arm']
        if arm not in spec['arms'] or arm in manifests or not c['freeze_trunk'] or c['extension_protocol_sha256']!=sha(protocol):raise ValueError('Wrong quality arm')
        if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or c['profile_only'] and not d['profile_qualified']:raise ValueError('Unaudited quality training')
        manifests[arm]=m;reports[arm]=d;paths[arm]=run;sources.append(dict(arm=arm,run=str(run.resolve()),manifest_sha256=sha(mp),report_sha256=sha(rp)))
    if set(manifests)!=set(spec['arms']):raise ValueError('Incomplete quality comparison')
    configs=[m['config'] for m in manifests.values()]
    for key in ('checkpoint_sha256','fragments_sha256','condition_selection_sha256','seed','batches','latent_motif_weight','motif_mass','profile_only','evaluation_steps','total_prior_updates'):
        if configs[0][key]!=configs[1][key]:raise ValueError('Changed matched setting '+key)
    updates=compare_quality_traces(manifests);reference=next(iter(paths.values()))/'evaluation_0.h5'
    result=dict(status='complete',profile_only=configs[0]['profile_only'],protocol_sha256=sha(protocol),sources=sources,
                matched_training_updates=updates,initial_predictions={arm:initial_parity(reference,run/'evaluation_0.h5') for arm,run in paths.items()},
                arms={arm:{k:d[k] for k in ('training_seconds','evaluation_seconds','elapsed_seconds','max_reserved_GiB','total_training_updates','summaries')} for arm,d in reports.items()},
                scope='Same proteins, initial predictions, frozen generator, RNG and LR draws. Condition identity differs exactly as preregistered; counts/lengths/placement margins match. Quality is not inferred from evaluation outcomes.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    view={k:v for k,v in result.items() if k!='arms'};a.output.with_suffix('.md').write_text('# Matched fragment-quality training\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(view))


if __name__=='__main__':main()
