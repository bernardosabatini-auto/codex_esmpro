"""One fixed fresh seed, sixteen matched noises, two guidance strengths."""
import argparse
import json
import time
from pathlib import Path

import h5py
import numpy as np
import torch

from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from prepare_fragment_repetition import audit_config
from prepare_overfit import sha
from profile_gpu import atomic_json
from train_fragment_conditioning import load_data


def main():
    p = argparse.ArgumentParser()
    for key in ('source', 'config', 'output'):
        p.add_argument('--' + key, type=Path, required=True)
    a = p.parse_args()
    c = json.loads(a.config.read_text())
    audit_config(c)
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    m = dict(status='running', config=c, controls=[], batches=[], training_updates=0)
    atomic_json(a.output / 'manifest.json', m)
    try:
        torch.set_num_threads(4)
        torch.cuda.set_device(0)
        torch.cuda.set_per_process_memory_fraction(.85)
        model, _ = load_legacy(c['checkpoint'], trusted_pickle=True)
        model.cuda().eval().requires_grad_(False)
        ck = torch.load(c['checkpoint'], map_location='cpu', weights_only=False, mmap=True)
        adapter = FragmentGeometryAdapter(model.d_model, n_layers=len(model.blocks),
            n_heads=model.n_heads, distance_precision='fp64').cuda().eval().requires_grad_(False)
        adapter.load_state_dict(ck['fragment_adapter'])
        decoder = load_proteinae(a.source / 'ProteinAE_v1', Path(c['decoder_checkpoint']),
                                steps=c['decoder_steps']).cuda().eval()
        v = load_data(c['fragments'], ck['experiment'].get('fragment_representation',
                      'latent_geometry'))['development', c['target_id']]
        q, n = v['conditions'][c['condition']], v['length']

        def sample(seed, indices, guidance, posed=False, decode=True):
            if time.monotonic() - start > c['work_cap_seconds']:
                raise TimeoutError('Repetition work cap')
            size = len(indices)
            mask = torch.ones(size, n, dtype=torch.bool, device='cuda')
            features = q['features'][None].expand(size, -1, -1).cuda()
            keep = q['keep'][None].expand(size, -1).cuda()
            coords = q['coordinates'][None].expand(size, -1, -1).cuda()
            if posed:
                coords = coords.double()
                rotation = coords.new_tensor([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
                coords = (coords @ rotation + coords.new_tensor([11, 7, -3])) * keep[..., None]
            noise = torch.cat([target_noise([c['target_id']], [n], 8, seed=seed,
                sample_index=k, stream='flow:0', device='cuda') for k in indices])
            z = sample_fragment(model, adapter, features, keep, mask, noise=noise,
                                steps=c['steps'], coordinates=coords, guidance=guidance)
            if not decode:
                return z.cpu().numpy(), None
            dn = torch.cat([target_noise([c['target_id']], [4*n], 3, seed=seed,
                sample_index=k, stream='decoder:0', device='cuda') for k in indices]) * decoder.fm.scale_ref
            _, bb = decoder(z, mask, noise=dn, return_backbone=True)
            return z.cpu().numpy(), bb.cpu().numpy()

        with torch.no_grad(), inference_precision('fp32'), h5py.File(c['historical_predictions']) as old, h5py.File(a.output / 'predictions.h5', 'x') as out:
            for guidance in c['guidance']:
                z, bb = sample(c['historical_seed'], list(range(4)), guidance)
                g = old[f'guidance{guidance}/{c["target_id"]}']
                expected = g['backbone'][:]
                metrics = [ca_metrics(x[:, 1], y[:, 1]) for x, y in zip(bb, expected)]
                control = dict(kind='historical', guidance=guidance,
                    latent_max_abs=float(np.max(abs(z - g['latent'][:]))),
                    max_ca_rmsd=max(r['ca_rmsd'] for r in metrics),
                    min_ca_lddt=min(r['ca_lddt'] for r in metrics),
                    same_validity=bool(np.array_equal(backbone_geometry(bb)['coarse_valid'],
                                                     backbone_geometry(expected)['coarse_valid'])))
                m['controls'].append(control)
                if control['latent_max_abs'] > 1e-5 or control['max_ca_rmsd'] > .2 or control['min_ca_lddt'] < .99 or not control['same_validity']:
                    raise ValueError('Historical reproduction failed')
                hg = out.create_group(f'historical/guidance{guidance}')
                hg.create_dataset('latent', data=z)
                hg.create_dataset('backbone', data=bb)
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                tick = time.monotonic()
                z, bb = sample(c['seed'], list(range(c['samples'])), guidance)
                torch.cuda.synchronize()
                m['batches'].append(dict(guidance=guidance, seconds=time.monotonic()-tick,
                                        peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30))
                g = out.create_group(f'guidance{guidance}/{c["target_id"]}')
                g.create_dataset('latent', data=z)
                g.create_dataset('backbone', data=bb)
                chunks = np.concatenate([sample(c['seed'], list(range(k, k+4)), guidance,
                                               decode=False)[0] for k in range(0, c['samples'], 4)])
                err = float(np.max(abs(z-chunks)))
                m['controls'].append(dict(kind='batch_partition', guidance=guidance, latent_max_abs=err))
                out.create_dataset(f'controls/partition{guidance}', data=chunks)
                if err > 1e-4:
                    raise ValueError('Batch partition parity failed')
                if guidance == 2:
                    posed, _ = sample(c['seed'], list(range(c['samples'])), guidance, posed=True, decode=False)
                    err = float(np.max(abs(z-posed)))
                    m['controls'].append(dict(kind='pose', guidance=guidance, latent_max_abs=err))
                    out.create_dataset('controls/pose2', data=posed)
                    if err > 1e-4:
                        raise ValueError('Exact pose parity failed')
                out.flush()
                atomic_json(a.output / 'manifest.json', m)
                print('Completed guidance', guidance, flush=True)
        m.update(status='complete', predictions_sha256=sha(a.output / 'predictions.h5'))
    except BaseException as error:
        m.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        m['elapsed_seconds'] = time.monotonic() - start
        atomic_json(a.output / 'manifest.json', m)


if __name__ == '__main__':
    main()
