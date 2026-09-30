"""Isolate padding, batching, and flow/decoder precision on fixed real inputs."""
import argparse
import gc
import json
import os
from pathlib import Path
import time
import torch
from latentfold.batching import prediction_batch
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig, sample
from latentfold.metrics import ca_metrics
from profile_gpu import atomic_json


def precision(mode):
    torch.set_float32_matmul_precision('highest' if mode == 'fp32' else 'high')
    return torch.autocast('cuda', dtype=torch.bfloat16, enabled=mode == 'bf16')


def compare(pred, reference, truth):
    out = ca_metrics(pred, reference)
    out['reference_ca_lddt_absolute_change'] = abs(ca_metrics(pred, truth)['ca_lddt'] -
                                                  ca_metrics(reference, truth)['ca_lddt'])
    out['passes'] = out['ca_rmsd'] <= 0.2 and out['ca_lddt'] >= 0.99 and out['reference_ca_lddt_absolute_change'] <= 0.005
    return out


@torch.no_grad()
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--minutes', type=float, default=8)
    p.add_argument('--large-batch', type=int, default=64)
    p.add_argument('--allow-gpu', action='store_true')
    a = p.parse_args()
    if not a.allow_gpu or a.large_batch < 2 or a.large_batch % 2:
        p.error('requires --allow-gpu and an even large batch >=2')
    a.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(8)
    torch.cuda.set_device(0)
    deadline = time.monotonic()+a.minutes*60
    report = dict(status='running', job_id=os.environ.get('SLURM_JOB_ID'), started_unix=time.time(),
                  targets=['3pnr_B', '5eft_B'], rows=[], flow_rows=[], timings=[],
                  note='Fixed per-target flow and decoder noise; FP32 disables TF32; thresholds unchanged')
    save = lambda: atomic_json(a.output/'diagnosis.json', report)
    def budget():
        if time.monotonic() > deadline:
            raise TimeoutError('diagnostic time budget exceeded')
    save()
    try:
        records = [read_record(a.source/'data/phase1_dataset/dataset_exp_val_esmc.h5', 'val', name,
                               embedding_dim=2560) for name in report['targets']]
        print('Loading decoder', flush=True)
        decoder = load_proteinae(a.source/'ProteinAE_v1', a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        requests = [(r, 0) for r in records]
        layouts = {}
        for i, r in enumerate(records):
            for label, length in [('exact', len(r['sequence'])), ('padded', 256)]:
                layouts[f'single_{label}_{i}'] = (prediction_batch([requests[i]], length, seed=0,
                                                    decoder_scale=decoder.fm.scale_ref), [i])
        base = prediction_batch(requests, 256, seed=0, decoder_scale=decoder.fm.scale_ref)
        layouts['batch2'] = (base, [0, 1])
        # Exact duplicate inputs test batch shape effects without changing RNG.
        layouts[f'batch{a.large_batch}'] = (tuple(x.repeat(a.large_batch//2, *([1]*(x.ndim-1))) for x in base),
                                             [0, 1]*(a.large_batch//2))
        for checkpoint in ['last_pf_459M_p128x8_long512_scratch.ckpt', 'best_lf_459M_nopair_long512_r4b.pt']:
            budget()
            print('Loading', checkpoint, flush=True)
            model, _ = load_legacy(a.source/'data/phase1_dataset'/checkpoint, trusted_pickle=True)
            model = model.cuda().eval().requires_grad_(False)
            for flow_precision in ['bf16', 'fp32']:
                latent = {}
                for layout, (tensors, indices) in layouts.items():
                    budget()
                    esm, mask, noise, dn = (x.cuda() for x in tensors)
                    torch.cuda.synchronize(); tick = time.perf_counter()
                    with precision(flow_precision):
                        z = sample(model, esm, mask, SampleConfig(steps=25, guidance=2), noise=noise)
                    torch.cuda.synchronize()
                    latent[layout] = z.cpu()
                    report['timings'].append(dict(checkpoint=checkpoint, stage='flow', precision=flow_precision,
                        layout=layout, seconds=time.perf_counter()-tick))
                    for position, i in enumerate(indices[:2]):
                        n = len(records[i]['sequence'])
                        reference = latent.get(f'single_exact_{i}')
                        if reference is not None:
                            delta = latent[layout][position, :n]-reference[0, :n]
                            report['flow_rows'].append(dict(checkpoint=checkpoint, precision=flow_precision, layout=layout,
                                target_id=records[i]['id'], rms_delta=float(delta.square().mean().sqrt()), max_abs_delta=float(delta.abs().max())))
                    del esm, mask, noise, dn, z
                    save()
                for decoder_precision in ['bf16', 'fp32']:
                    decoded = {}
                    for layout, (tensors, indices) in layouts.items():
                        budget()
                        mask, dn = tensors[1].cuda(), tensors[3].cuda()
                        z = latent[layout].cuda()
                        torch.cuda.synchronize(); tick = time.perf_counter()
                        with precision(decoder_precision):
                            ca = decoder(z, mask, noise=dn).float().cpu().numpy()
                        report['timings'].append(dict(checkpoint=checkpoint, stage='decoder', precision=decoder_precision,
                            layout=layout, seconds=time.perf_counter()-tick))
                        decoded[layout] = ca
                        for position, i in enumerate(indices[:2]):
                            n = len(records[i]['sequence'])
                            reference = decoded.get(f'single_exact_{i}')
                            if reference is not None:
                                row = dict(checkpoint=checkpoint, flow_precision=flow_precision, decoder_precision=decoder_precision,
                                    layout=layout, stage='full_pipeline', target_id=records[i]['id'],
                                    **compare(ca[position, :n], reference[0, :n], records[i]['ca'].numpy()))
                                report['rows'].append(row); print(json.dumps(row), flush=True)
                        if layout.startswith('batch'):
                            # Hold the latent values exactly fixed to isolate decoder batching.
                            fixed_z = torch.zeros_like(z)
                            for position, i in enumerate(indices):
                                n = len(records[i]['sequence'])
                                fixed_z[position, :n] = latent[f'single_exact_{i}'][0, :n].cuda()
                            with precision(decoder_precision):
                                fixed_ca = decoder(fixed_z, mask, noise=dn).float().cpu().numpy()
                            for position, i in enumerate(indices[:2]):
                                n = len(records[i]['sequence'])
                                row = dict(checkpoint=checkpoint, flow_precision=flow_precision, decoder_precision=decoder_precision,
                                    layout=layout, stage='decoder_fixed_latent', target_id=records[i]['id'],
                                    **compare(fixed_ca[position, :n], decoded[f'single_exact_{i}'][0, :n], records[i]['ca'].numpy()))
                                report['rows'].append(row); print(json.dumps(row), flush=True)
                            del fixed_z
                        del z, mask, dn
                        save()
                del latent
            del model
            gc.collect(); torch.cuda.empty_cache()
        report['status'] = 'complete'
    except BaseException as error:
        report['status'], report['error'] = 'failed', f'{type(error).__name__}: {error}'
        raise
    finally:
        report['ended_unix'] = time.time()
        save()


if __name__ == '__main__':
    main()
