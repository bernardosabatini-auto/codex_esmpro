"""Paired FP32 fold timing with and without unused confidence outputs."""
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import time
import h5py
import torch
from latentfold.coordinates_only import coordinates_only
from latentfold.precision import inference_precision
from latentfold.teacher import fast_features, load_fast_model
from benchmark_esmfold2 import backbone_indices
from profile_gpu import Telemetry, atomic_json
from teacher_coordinates_profile_core import audit, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    c = json.loads(a.config.read_text()); protocol = audit(c)
    a.output.mkdir(parents=True, exist_ok=False)
    m = dict(status='running', config=c, records=[], training_updates_executed=0,
             new_design_attempts=0, config_sha256=sha(a.config))
    start = time.monotonic(); telemetry = None
    try:
        torch.set_num_threads(4); torch.cuda.set_device(0)
        torch.cuda.set_per_process_memory_fraction(.85)
        torch.use_deterministic_algorithms(True)
        telemetry = Telemetry(a.output)
        model, m['teacher_adapter'] = load_fast_model(Path(c['teacher_artifacts'][0]['path']).parent)
        original = model.confidence_head
        # Full model fingerprints would add unnecessary large transfers; check
        # all parameter identities/versions and head identity after each call.
        before = [(name, id(v), v._version) for name, v in model.named_parameters()]
        with torch.no_grad(), inference_precision('fp32'), h5py.File(a.output/'coordinates.h5', 'x') as f:
            for entry_index, entry in enumerate(c['entries']):
                group = f.create_group(str(entry_index))
                for repeat in range(protocol['repeats_including_warmup']):
                    arms = ('full', 'coordinates') if (entry_index + repeat) % 2 == 0 else ('coordinates', 'full')
                    for arm in arms:
                        if time.monotonic() - start > protocol['work_cap_seconds']:
                            raise TimeoutError('Bounded coordinate profile exhausted')
                        torch.manual_seed(entry['seed']); torch.cuda.synchronize()
                        torch.cuda.reset_peak_memory_stats(); tick = time.monotonic()
                        features = fast_features(entry['sequence'])
                        indices = backbone_indices(features, entry['length'])
                        with coordinates_only(model) if arm == 'coordinates' else nullcontext():
                            output = model.fold(**features, num_loops=3, num_sampling_steps=50, num_diffusion_samples=1)
                            coords = output.sample_atom_coords.float().cpu().numpy()
                            del output
                        torch.cuda.synchronize(); seconds = time.monotonic() - tick
                        if model.confidence_head is not original:
                            raise ValueError('Confidence module was not restored')
                        dataset = f'{arm}_{repeat}'; group.create_dataset(dataset, data=coords)
                        if repeat == 0 and arm == 'full': group.create_dataset('backbone_indices', data=indices)
                        m['records'].append(dict(entry_index=entry_index, arm=arm, repeat=repeat,
                            dataset=f'{entry_index}/{dataset}', seconds=seconds,
                            peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                            peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                            rng_after=hashlib.sha256(torch.cuda.get_rng_state().cpu().numpy().tobytes()).hexdigest()))
                        atomic_json(a.output/'manifest.json', m)
                print('profiled', entry['bucket'], entry['sequence_index'], flush=True)
            after = [(name, id(v), v._version) for name, v in model.named_parameters()]
            m['parameters_unchanged'] = before == after
            if not m['parameters_unchanged']: raise ValueError('Model parameters changed')
        m['status'] = 'complete'
    except BaseException as error:
        m.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if telemetry: telemetry.close()
        m['elapsed_seconds'] = time.monotonic() - start
        atomic_json(a.output/'manifest.json', m)


if __name__ == '__main__': main()
