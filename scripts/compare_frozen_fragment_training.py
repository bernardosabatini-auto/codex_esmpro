"""Match learned-generator freezing to the already completed full-network controls."""
import argparse
import json
from pathlib import Path

from compare_broad_fragment_training import compare_traces, initial_parity
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runs',type=Path,nargs=2,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_frozen_trunk_protocol.json'
    spec=json.loads(protocol.read_text());new={};reports={};manifests={};runs={};sources=[]
    for run in args.runs:
        run=run.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
        m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];arm=c['extension_arm']
        if arm not in spec['arms'] or arm in new or not c.get('freeze_trunk') or c['extension_protocol_sha256']!=sha(protocol):
            raise ValueError('Wrong or duplicate frozen arm')
        new[arm]=run;manifests[arm]=m;reports[arm]=d;runs[arm]=run
    if set(new)!=set(spec['arms']) or len({m['config']['profile_only'] for m in manifests.values()})!=1:
        raise ValueError('Incomplete frozen comparison')
    profile=next(iter(manifests.values()))['config']['profile_only']
    for arm,name in spec['legacy_full_profiles' if profile else 'legacy_full_runs'].items():
        run=root/'runs'/name;runs[arm]=run
        manifests[arm]=json.loads((run/'manifest.json').read_text())
        reports[arm]=json.loads((root/'reports'/(name+'.json')).read_text())
        c=manifests[arm]['config']
        if c.get('freeze_trunk') or c['extension_arm']!=arm or c['motif_mass'] is not None:
            raise ValueError('Wrong completed full-network control')
    for arm,m in manifests.items():
        run=runs[arm];mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');d=reports[arm]
        if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or m['config']['profile_only']!=profile or profile and not d['profile_qualified']:
            raise ValueError('Unaudited training arm')
        sources.append(dict(arm=arm,run=str(run),manifest_sha256=sha(mp),report_sha256=sha(rp)))
    for corpus in ('control512','broad'):
        configs=[m['config'] for m in manifests.values() if m['config']['corpus']==corpus]
        if len(configs)!=2:raise ValueError('Both update policies required per corpus')
        for key in ('checkpoint_sha256','fragments_sha256','latent_motif_weight','motif_mass','seed','batches','evaluation_steps','total_prior_updates'):
            if configs[0][key]!=configs[1][key]:raise ValueError('Changed matched setting '+key)
    updates=compare_traces(manifests)
    reference=runs['control_weight3']/'evaluation_0.h5'
    controls={arm:initial_parity(reference,run/'evaluation_0.h5') for arm,run in new.items()}
    result=dict(status='complete',profile_only=profile,protocol_sha256=sha(protocol),
                matched_training_updates=updates,initial_predictions=controls,sources=sources,
                arms={arm:{k:d[k] for k in ('training_seconds','evaluation_seconds','elapsed_seconds','max_reserved_GiB','total_training_updates','summaries')} for arm,d in reports.items()},
                scope='Only fragment adapters update in the new arms. Reused full-network controls retain original reports and budgets. Initial outputs, training exposure and RNG traces must match.')
    atomic_json(args.output.with_suffix('.json'),result)
    view={k:v for k,v in result.items() if k!='arms'}
    args.output.with_suffix('.md').write_text('# Learned-generator freezing comparison\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')
    print(json.dumps({k:result[k] for k in ('status','matched_training_updates','initial_predictions')}))


if __name__=='__main__':main()
