"""Collect a predeclared accuracy/cost sweep; score later on CPUs.

One checkpoint per GPU process. All embeddings are read once on the host.
Output contains every target/sample, with no oracle selection. Throughput
excludes ESMC and does not support an end-to-end sequence-folding speed claim.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import time

import h5py
import numpy as np
import torch

from latentfold.batching import requests_by_bucket, prediction_batch
from latentfold.checkpoints import load_legacy
from latentfold.data import read_ids, read_record
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig, sample
from latentfold.metrics import ca_metrics
from predict import file_identity
from profile_gpu import Telemetry, atomic_json


@torch.no_grad()
def infer(model, decoder, tensors, cfg):
    esm, mask, noise, dn = (x.to('cuda', non_blocking=True) for x in tensors)
    with torch.autocast('cuda', dtype=torch.bfloat16):
        z = sample(model, esm, mask, cfg, noise=noise)
        ca, backbone = decoder(z.float(), mask, return_backbone=True, noise=dn)
    if not torch.isfinite(backbone).all():
        raise FloatingPointError('nonfinite coordinates')
    return z, ca, backbone


def batching_controls(model, decoder, buckets, seed):
    """Check real-weight padded/batched predictions against unpadded singles."""
    rows = []
    cfg = SampleConfig(steps=25, guidance=2)
    for length, requests in buckets.items():
        unique = {r['id']: r for r, _ in requests}
        if not unique:
            continue
        ordered = list(unique.values())
        selected = [ordered[0]] if len(ordered) == 1 else [ordered[0], ordered[-1]]
        controls = [(r, 0) for r in selected]
        tensors = prediction_batch(controls, length, seed=seed, decoder_scale=decoder.fm.scale_ref)
        _, ca, _ = infer(model, decoder, tensors, cfg)
        whole = ca.float().cpu().numpy()
        del ca
        for i, request in enumerate(controls):
            r, _ = request
            n = len(r['sequence'])
            single = prediction_batch([request], n, seed=seed, decoder_scale=decoder.fm.scale_ref)
            _, ca, _ = infer(model, decoder, single, cfg)
            alone = ca[0].float().cpu().numpy()
            metrics = ca_metrics(whole[i, :n], alone)
            delta = abs(ca_metrics(whole[i, :n], r['ca'].numpy())['ca_lddt'] -
                        ca_metrics(alone, r['ca'].numpy())['ca_lddt'])
            row = dict(target_id=r['id'], padded_length=length,
                       reference_ca_lddt_absolute_change=delta, **metrics)
            rows.append(row)
            print('batching_control', json.dumps(row), flush=True)
            if metrics['ca_rmsd'] > 0.2 or metrics['ca_lddt'] < 0.99 or delta > 0.005:
                raise RuntimeError(f"batching/precision control failed: {r['id']}: {row}")
    return rows


def write_batch(h5, key, requests, z, ca, backbone):
    group = h5.require_group(key)
    for i, (record, k) in enumerate(requests):
        name = hashlib.sha256(record['id'].encode()).hexdigest()
        target = group.require_group(name)
        target.attrs['target_id'] = record['id']
        target.attrs['sequence_sha256'] = record['sequence_sha256']
        n = len(record['sequence'])
        sample_group = target.create_group(str(k))  # duplicate writes are errors
        sample_group.create_dataset('z', data=z[i, :n])
        sample_group.create_dataset('ca', data=ca[i, :n])
        sample_group.create_dataset('backbone', data=backbone[i, :n])
    h5.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--nsys-metrics', action='store_true')
    parser.add_argument('--allow-gpu', action='store_true')
    a = parser.parse_args()
    if not a.allow_gpu:
        parser.error('--allow-gpu is required')
    config = json.loads(a.config.read_text())
    entry = config['models'][a.model]
    ids_file = a.config.parent / config['target_manifest']
    ids = read_ids(ids_file)
    if len(ids) != config['expected_targets']:
        raise ValueError('target count differs from predeclared comparison')
    if hashlib.sha256(ids_file.read_bytes()).hexdigest() != config['target_manifest_sha256']:
        raise ValueError('target manifest was changed')
    batches = {int(k): int(v) for k, v in entry['batches'].items()}
    if not batches or min(batches.values()) < 1:
        raise ValueError('invalid batch sizes')
    a.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(8)
    torch.set_float32_matmul_precision('high')
    torch.cuda.set_device(0)
    torch.manual_seed(config['seed'])
    started = time.time()
    deadline = time.monotonic() + config['internal_minutes']*60
    manifest = dict(status='running', config=config, model=a.model,
                    source=str(a.source.resolve()),
                    job_id=os.environ.get('SLURM_JOB_ID'), started_unix=started,
                    torch=torch.__version__, gpu=torch.cuda.get_device_name(0),
                    timing_scope='cached embeddings to CA, bf16; ESMC excluded',
                    batches=[], completed_predictions=0)
    telemetry = None
    save = lambda: atomic_json(a.output/'manifest.json', manifest)
    save()
    try:
        telemetry = Telemetry(a.output, a.nsys_metrics)
        manifest['telemetry'] = telemetry.info
        h5 = a.source/'data/phase1_dataset/dataset_exp_val_esmc.h5'
        print(f'Reading {len(ids)} cached records', flush=True)
        records = [read_record(h5, 'val', name, embedding_dim=2560) for name in ids]
        manifest['dataset'] = file_identity(h5)
        buckets = requests_by_bucket(records, batches, config['samples'])
        checkpoint = a.source/'data/phase1_dataset'/entry['checkpoint']
        manifest['checkpoint'] = file_identity(checkpoint, hash_contents=True)
        model, arch = load_legacy(checkpoint, trusted_pickle=True)
        model = model.cuda().eval().requires_grad_(False)
        manifest['architecture'] = arch
        ae_checkpoint = a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt'
        manifest['decoder_checkpoint'] = file_identity(ae_checkpoint, hash_contents=True)
        decoder = load_proteinae(a.source/'ProteinAE_v1', ae_checkpoint,
                                 steps=config['decoder_steps']).cuda()
        manifest['controls'] = batching_controls(model, decoder, buckets, config['seed'])
        manifest['ready_unix'] = time.time()
        save()
        print('Controls passed. Starting full comparison.', flush=True)
        with h5py.File(a.output/'predictions.h5', 'x') as output, ThreadPoolExecutor(max_workers=1) as writer:
            pending = None
            for steps in config['flow_steps']:
                for guidance in config['guidance']:
                    cfg = SampleConfig(steps=steps, guidance=guidance)
                    key = f'steps{steps}_cfg{guidance:g}'
                    for length, requests in buckets.items():
                        if not requests:
                            continue
                        count = batches[length]
                        for offset in range(0, len(requests), count):
                            if time.monotonic() >= deadline:
                                raise TimeoutError('internal time budget reached; incomplete comparison')
                            chunk = requests[offset:offset+count]
                            wall_start = time.perf_counter()
                            tensors = prediction_batch(chunk, length, seed=config['seed'],
                                                       decoder_scale=decoder.fm.scale_ref)
                            tensors = tuple(x.pin_memory() for x in tensors)
                            torch.cuda.synchronize()
                            torch.cuda.reset_peak_memory_stats()
                            nvtx = f'collect::{key}::L{length}::offset{offset}'
                            torch.cuda.nvtx.range_push(nvtx)
                            tick = time.perf_counter()
                            try:
                                z, ca, backbone = infer(model, decoder, tensors, cfg)
                                torch.cuda.synchronize()
                            finally:
                                torch.cuda.nvtx.range_pop()
                            gpu_seconds = time.perf_counter()-tick
                            z_cpu, ca_cpu = z.float().cpu().numpy(), ca.float().cpu().numpy()
                            bb_cpu = backbone.float().cpu().numpy()
                            del z, ca, backbone, tensors
                            if pending is not None:
                                pending[0].result()
                                manifest['completed_predictions'] += pending[1]
                            pending = (writer.submit(write_batch, output, key, chunk, z_cpu, ca_cpu, bb_cpu), len(chunk))
                            manifest['batches'].append(dict(setting=key, length=length, batch=len(chunk),
                                nvtx_range=nvtx, gpu_seconds_including_h2d=gpu_seconds,
                                seconds_including_input_and_d2h=time.perf_counter()-wall_start,
                                padding_fraction=1-sum(len(r['sequence']) for r, _ in chunk)/(len(chunk)*length),
                                peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                                peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                            save()
                        print(key, length, 'complete', flush=True)
            if pending:
                pending[0].result()
                manifest['completed_predictions'] += pending[1]
        expected = len(ids)*config['samples']*len(config['flow_steps'])*len(config['guidance'])
        if manifest['completed_predictions'] != expected:
            raise ValueError('incomplete target/sample coverage')
        manifest['status'] = 'complete'
    except BaseException as error:
        manifest['status'], manifest['error'] = 'failed', f'{type(error).__name__}: {error}'
        raise
    finally:
        if telemetry:
            telemetry.close()
        manifest['ended_unix'] = time.time()
        save()


if __name__ == '__main__':
    main()
