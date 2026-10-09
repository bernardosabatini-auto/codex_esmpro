"""Independent CPU inventory, paired draws, checkpoint and export audit."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
import torch
from prepare_overfit import sha
from train_fragment_context_flow import digest, load_data


def analyze(run):
    mp = run/'manifest.json'; m = json.loads(mp.read_text()); c = m['config']
    if m['status'] != 'complete':
        return dict(status='failed', qualified=False, error=m.get('error', 'incomplete'), manifest_sha256=sha(mp))
    data, arrays = load_data(c); spec = data['spec']
    for source in data['sources']:
        if sha(source['path']) != source['sha256']:
            raise ValueError('Original source/protocol changed')
    families = {s: {r['family'] for r in data['records'] if r['split'] == s} for s in data['counts']}
    if any(families[a]&families[b] for a,b in [('train','validation'),('train','evaluation'),('validation','evaluation')]):
        raise ValueError('Family leakage')
    if set(m['arms']) != set(spec['arms']):
        raise ValueError('Missing paired arm')
    x, y = (m['arms'][arm] for arm in spec['arms'])
    if x['draws'] != y['draws'] or x['initial_hash'] != y['initial_hash'] or len(x['draws']) != c['updates']:
        raise ValueError('Unmatched training')
    if x['initial_validation_loss'] != y['initial_validation_loss']:
        raise ValueError('Initial predictions differ')
    # Independently reproduce every CPU minibatch/noise/time draw.
    rng = torch.Generator().manual_seed(spec['seed']+1)
    for expected in x['draws']:
        ids = torch.randint(len(arrays['train_features']), (spec['batch'],), generator=rng)
        noise = torch.randn(spec['batch'],20,8,generator=rng); times = torch.rand(spec['batch'],generator=rng)
        if digest(dict(ids=ids,noise=noise,times=times)) != expected:
            raise ValueError('Draw replay failed')
    summaries = {}
    for arm, r in m['arms'].items():
        cp = run/(arm+'.pt'); sample = run/(arm+'_codes.npy')
        if sha(cp) != r['checkpoint_sha256'] or sha(sample) != r['codes_sha256'] or not r['reload_exact']:
            raise ValueError('Changed or failed checkpoint/sample')
        checkpoint = torch.load(cp,map_location='cpu',weights_only=True)
        if checkpoint['spec'] != spec or checkpoint['data_manifest_sha256'] != c['data_manifest_sha256']:
            raise ValueError('Checkpoint provenance mismatch')
        if c['profile_only'] and (digest(checkpoint['model']) != r['prefix']['raw'] or digest(checkpoint['ema']) != r['prefix']['ema']):
            raise ValueError('Profile checkpoint hash mismatch')
        codes = np.load(sample,allow_pickle=False)
        if codes.shape != (128,20,8) or not np.isfinite(codes).all():
            raise ValueError('Wrong sampled code inventory')
        if len(r['losses']) != c['updates'] or not all(math.isfinite(v) for v in r['losses']+r['validation_loss']):
            raise ValueError('Missing/nonfinite losses')
        if (arm == 'isolated' and min(r['sensitivity'],r['max_condition_gradient']) <= 0
                or arm == 'ablated' and max(r['sensitivity'],r['max_condition_gradient']) != 0):
            raise ValueError('Conditioning control failed')
        summaries[arm] = {k:r[k] for k in ('prefix','training_seconds','peak_reserved_GiB','parameters','sensitivity','checkpoint_sha256','codes_sha256')}
        summaries[arm].update(initial_loss=float(np.mean(r['initial_validation_loss'])),
                              final_validation_loss=float(np.mean(r['validation_loss'])),
                              final_training_loss=float(np.mean(r['losses'][-20:])),
                              mean_per_target_code_std=float(codes.reshape(32,4,20,8).std(1).mean()))
    if not c['profile_only']:
        if sha(c['profile_report']) != c['profile_report_sha256']:
            raise ValueError('Changed technical qualification')
        profile = json.loads(Path(c['profile_report']).read_text())
        if not profile['qualified'] or profile['data_manifest_sha256'] != c['data_manifest_sha256']:
            raise ValueError('Invalid full lineage')
        if any(summaries[arm]['prefix'] != profile['arms'][arm]['prefix'] for arm in spec['arms']):
            raise ValueError('Full/profile prefix mismatch')
    seconds = sum(r['training_seconds'] for r in m['arms'].values())
    minutes = max(5,math.ceil((1.5*seconds*spec['updates']/c['updates']+180)/60))
    qualified = max(r['peak_reserved_GiB'] for r in m['arms'].values()) < 75 and minutes <= 60
    return dict(status='complete',qualified=qualified,profile_only=c['profile_only'],updates=c['updates'],
                data_manifest_sha256=c['data_manifest_sha256'],manifest_sha256=sha(mp),counts=data['counts'],
                arms=summaries,recommended_full_minutes=minutes,elapsed_seconds=m['elapsed_seconds'],
                interpretation='Technical qualification only; loss and sampled latent diversity do not establish structural designability.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if len(a.runs)!=1:raise ValueError('One paired run required')
    torch.set_num_threads(1);d=analyze(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    short={k:v for k,v in d.items() if k!='arms'}
    short['arms']={arm:{k:v for k,v in r.items() if k!='prefix'} for arm,r in d.get('arms',{}).items()}
    a.output.with_suffix('.md').write_text('# Isolated-fragment context-code flow\n\n```json\n'+json.dumps(short,indent=2)+'\n```\n')
    print(json.dumps(short))


if __name__=='__main__':main()
