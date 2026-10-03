"""Replay one failed numerical control; never score these as design attempts."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import time
import warnings

import h5py
import numpy as np
import torch

from benchmark_esmfold2 import backbone_indices
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from latentfold.teacher import fast_features, load_fast_model
from prepare_overfit import sha
from profile_gpu import atomic_json


def tensor_hash(tensor):
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def feature_hashes(features):
    return {k: tensor_hash(v) if isinstance(v, torch.Tensor) else v for k, v in features.items()}


def rng_hashes():
    return [tensor_hash(torch.get_rng_state()), tensor_hash(torch.cuda.get_rng_state())]


def main():
    p = argparse.ArgumentParser()
    for key in ('config', 'output'):
        p.add_argument('--' + key, type=Path, required=True)
    a = p.parse_args()
    c = json.loads(a.config.read_text())
    if sha(c['failed_manifest']) != c['failed_manifest_sha256'] or sha(c['failed_refolded']) != c['failed_refolded_sha256']:
        raise ValueError('Changed failed-run evidence')
    old = json.loads(Path(c['failed_manifest']).read_text())
    if old['status'] != 'failed' or old['error'] != 'ValueError: Teacher repeatability failed' or len(old['records']) != 1:
        raise ValueError('Unexpected diagnostic source')
    for dep in old['config']['teacher_artifacts']:
        if sha(dep['path']) != dep['sha256']:
            raise ValueError('Changed teacher artifact')
    first = old['records'][0]
    seq = old['sequences'][first['name']][first['sequence_index']]
    seed = first['seed']
    a.output.mkdir(parents=True, exist_ok=False)
    m = dict(status='running', config=c, seed=seed, sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),
             records=[], comparisons=[], strict_probe={}, design_attempts=0,
             scope='Numerical diagnostic only; all calls retained, no best repeat or qualification retry.',
             environment={k: os.environ.get(k) for k in ('CUBLAS_WORKSPACE_CONFIG', 'PYTORCH_ALLOC_CONF')})
    atomic_json(a.output / 'manifest.json', m)
    start = time.monotonic()
    try:
        torch.set_num_threads(4)
        torch.cuda.set_device(0)
        torch.cuda.set_per_process_memory_fraction(.85)
        m['device'] = torch.cuda.get_device_name()
        model, m['teacher_adapter'] = load_fast_model(Path(c['source']) / 'data/esmfold2_fast')
        with h5py.File(c['failed_refolded']) as f:
            original = f[first['name']][str(first['sequence_index'])][:]
        outputs = []
        with torch.no_grad(), inference_precision('fp32'), h5py.File(a.output / 'replays.h5', 'x') as f:
            features = None
            for index in range(6):
                torch.manual_seed(seed)
                before_rng = rng_hashes()
                fresh = index == 0 or index >= 3
                if fresh:
                    features = fast_features(seq)
                after_rng = rng_hashes()
                before = feature_hashes(features)
                indices = backbone_indices(features, len(seq))
                tick = time.monotonic()
                output = model.fold(**features, num_loops=3, num_sampling_steps=50, num_diffusion_samples=1)
                bb = output.sample_atom_coords.float().cpu().numpy()[0, indices, :]
                del output
                if bb.shape != original.shape or not np.isfinite(bb).all():
                    raise ValueError('Invalid replay')
                f.create_dataset(str(index), data=bb)
                outputs.append(bb)
                m['records'].append(dict(index=index, fresh_features=fresh, seconds=time.monotonic()-tick,
                                         features_before=before, features_after=feature_hashes(features),
                                         rng_before_features=before_rng, rng_after_features=after_rng,
                                         original_comparison=ca_metrics(original[:, 1], bb[:, 1])))
                atomic_json(a.output / 'manifest.json', m)
            for left, right in itertools.combinations(range(6), 2):
                m['comparisons'].append(dict(left=left, right=right, **ca_metrics(outputs[left][:, 1], outputs[right][:, 1])))
            # Surface unsupported nondeterministic kernels without changing the six baseline calls.
            torch.manual_seed(seed)
            torch.use_deterministic_algorithms(True, warn_only=True)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                try:
                    output = model.fold(**fast_features(seq), num_loops=3, num_sampling_steps=50, num_diffusion_samples=1)
                    probe = output.sample_atom_coords.float().cpu().numpy()[0, indices, :]
                    f.create_dataset('deterministic_warning_probe', data=probe)
                    m['strict_probe']['comparison'] = ca_metrics(outputs[0][:, 1], probe[:, 1])
                    del output
                except RuntimeError as error:
                    m['strict_probe']['error'] = str(error)
                m['strict_probe']['warnings'] = sorted(set(str(w.message) for w in caught))
            torch.use_deterministic_algorithms(False)
        m['status'] = 'complete'
    except BaseException as error:
        m.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        m['elapsed_seconds'] = time.monotonic() - start
        atomic_json(a.output / 'manifest.json', m)


if __name__ == '__main__':
    main()
