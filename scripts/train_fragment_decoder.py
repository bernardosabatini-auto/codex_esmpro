"""Train only explicit fragment residuals through the actual three-step decoder."""
import argparse
import json
import math
import time
from pathlib import Path

import h5py
import numpy as np
import torch

from latentfold.decoder import load_proteinae
from latentfold.fragment_decoder import FragmentDecoder, fragment_decoder_loss
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from evaluate_decoder_fragment_variance import check_backbones
from fragment_decoder_training_core import (audit, load_training, training_batch, panel,
    canonical_frozen_state, expected_frozen_state, initial_adapter)
from native_anchor_training_core import state_hash, tensor_hash
from prepare_overfit import sha
from profile_gpu import Telemetry, atomic_json


def main():
    p = argparse.ArgumentParser()
    for name in ('source', 'config', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    c = json.loads(a.config.read_text())
    spec = audit(c)
    data, selected = load_training(c), panel(c)
    items = load_conditions(c['fragments'], [r['id'] for r in selected], 'c20_center', cohort='train')
    initial_ids = [next(r['id'] for r in c['selected'] if r['bucket'] == b) for b in (128, 256, 384, 512)]
    a.output.mkdir(exist_ok=False)
    tick, telemetry = time.monotonic(), None
    m = dict(status='running', config=c, updates=0, training=[], initial_controls=[],
             controls=[], evaluations=[], checkpoint_replay=[])
    atomic_json(a.output/'manifest.json', m)
    try:
        torch.set_num_threads(2)
        torch.cuda.set_device(0)
        torch.cuda.set_per_process_memory_fraction(.85)
        torch.manual_seed(spec['seed'])
        codec = load_proteinae(a.source/'ProteinAE_v1', Path(c['decoder_checkpoint']), steps=3)
        model = FragmentDecoder(codec, seed=spec['seed']).cuda().eval()
        m['frozen_original'] = state_hash(expected_frozen_state(c))
        m['frozen_initial'] = state_hash(canonical_frozen_state(model))
        m['initial_adapter_sha256'] = state_hash(model.adapter.state_dict())
        if m['frozen_original'] != m['frozen_initial'] or m['initial_adapter_sha256'] != state_hash(initial_adapter(c)):
            raise ValueError('Changed pretrained decoder or zero adapter initialization')
        m['trainable_parameters'] = sum(p.numel() for p in model.parameters() if p.requires_grad)
        if m['trainable_parameters'] != sum(p.numel() for p in model.adapter.parameters()):
            raise ValueError('Unexpected trainable base parameters')
        telemetry = Telemetry(a.output, True)

        def evaluation_inputs(ident):
            item = items[ident]
            n = item['length']
            mask = torch.ones(4, n, dtype=torch.bool, device='cuda')
            features = item['features'][None].expand(4, -1, -1).cuda()
            keep = item['keep'][None].expand(4, -1).cuda()
            coords = item['coordinates'][None].expand(4, -1, -1).cuda()
            noise = torch.cat([target_noise([ident], [4*n], 3, seed=spec['sampling_seed'], sample_index=k,
                                           stream='decoder:0', device='cuda') for k in range(4)]) * model.scale_ref
            return features, keep, mask, coords, noise

        with torch.no_grad(), inference_precision('fp32'), h5py.File(c['baseline_predictions']) as old, \
                h5py.File(c['diagnostic_predictions']) as native, \
                h5py.File(a.output/'initial_masked.h5', 'x') as initial, h5py.File(a.output/'initial_clean.h5', 'x') as clean:
            for r in selected:
                ident = r['id']
                item = items[ident]
                features, keep, mask, coords, noise = evaluation_inputs(ident)
                contexts = dict(generated=torch.from_numpy(old['new/'+ident+'/latent'][:]).cuda(),
                                native=data[ident]['target'][None].expand(4, -1, -1).cuda())
                for kind, context in contexts.items():
                    z = torch.where(keep[..., None], torch.zeros_like(context), context)
                    expected = codec(z, mask, noise=noise, return_backbone=True)[1]
                    bb = model(context, features, keep, mask, coords, noise=noise)
                    error = float((bb-expected).abs().max())
                    if error > 1e-5:
                        raise ValueError('Zero decoder adapter changed masked decoding')
                    g = initial.create_group(kind+'/'+ident)
                    g['latent'], g['backbone'], g['original_backbone'] = z.cpu().numpy(), bb.cpu().numpy(), expected.cpu().numpy()
                    m['initial_controls'].append(dict(kind=kind+'_masked', target_id=ident, backbone_max_abs=error))
                    if ident in initial_ids:
                        expected = codec(context, mask, noise=noise, return_backbone=True)[1]
                        bb = model(context, features, keep, mask, coords, noise=noise, mask_fragment=False)
                        error = float((bb-expected).abs().max())
                        if error > 1e-5:
                            raise ValueError('Zero decoder adapter changed original decoding')
                        reference = old['new/'+ident+'/backbone'][:] if kind == 'generated' else native['native/'+ident+'/backbone'][:4]
                        check = check_backbones(bb.cpu().numpy(), reference, item['fragment'], item['start'], ident)
                        g = clean.create_group(kind+'/'+ident)
                        g['backbone'], g['original_backbone'] = bb.cpu().numpy(), expected.cpu().numpy()
                        m['initial_controls'].append(dict(kind=kind+'_clean', target_id=ident, backbone_max_abs=error, **check))
        m['initial_masked_sha256'], m['initial_clean_sha256'] = sha(a.output/'initial_masked.h5'), sha(a.output/'initial_clean.h5')

        # Validate checkpointing through the real external decoder at initialization.
        ident = initial_ids[0]
        values = [x.cuda() for x in training_batch(data, ident, ['c20_center'])]
        context, target, features, keep, mask, coords = values
        noise = evaluation_inputs(ident)[-1][:1]
        grads, predictions, losses = [], [], []
        model.train()
        from latentfold.fragment_decoder import weighted_backbone_mse, backbone_bond_mse
        with inference_precision('fp32'):
            for checkpointed in (False, True):
                model.zero_grad(set_to_none=True)
                bb = model(context, features, keep, mask, coords, noise=noise, checkpoint_steps=checkpointed)
                loss = weighted_backbone_mse(bb, target, keep) + backbone_bond_mse(bb, target)
                loss.backward()
                predictions.append(bb.detach())
                losses.append(float(loss.detach()))
                grads.append({k: p.grad.detach().clone() for k, p in model.adapter.named_parameters()})
            error = max(float((grads[0][k]-grads[1][k]).abs().max()) for k in grads[0])
            if (not torch.allclose(predictions[0], predictions[1], atol=1e-4, rtol=1e-4)
                    or any(not torch.allclose(grads[0][k], grads[1][k], atol=1e-4, rtol=1e-4) for k in grads[0])
                    or not math.isclose(losses[0], losses[1], abs_tol=1e-4, rel_tol=1e-4)
                    or any(p.grad is not None for p in model.decoder.parameters())
                    or grads[1]['output.weight'].norm() <= 0 or grads[1]['pair_output.weight'].norm() <= 0):
                raise ValueError('Actual decoder gradient/checkpoint control failed')
            m['gradient_control'] = dict(target_id=ident, prediction_max_abs=float((predictions[0]-predictions[1]).abs().max()),
                gradient_max_abs=error, losses=losses, token_gradient_norm=float(grads[1]['output.weight'].norm()),
                pair_gradient_norm=float(grads[1]['pair_output.weight'].norm()),
                prediction_tolerance_ratio=float(((predictions[0]-predictions[1]).abs()/(1e-4+1e-4*predictions[1].abs())).max()),
                gradient_tolerance_ratio=max(float(((grads[0][k]-grads[1][k]).abs()/(1e-4+1e-4*grads[1][k].abs())).max()) for k in grads[0]))
        del grads, predictions, values, context, target, features, keep, mask, coords, noise, loss, bb
        model.zero_grad(set_to_none=True)
        m['control_peak_reserved_GiB'] = torch.cuda.max_memory_reserved()/2**30
        atomic_json(a.output/'manifest.json', m)

        optimizer = torch.optim.AdamW(model.adapter.parameters(), lr=spec['learning_rate'], betas=(.9, .95), weight_decay=.01, foreach=False)
        ema = {k: v.detach().clone() for k, v in model.adapter.state_dict().items()}
        order = np.random.default_rng(spec['seed'])
        rng = torch.Generator(device='cuda').manual_seed(spec['seed'])
        buckets = {b: sorted(i for i, r in data.items() if r['bucket'] == b) for b in (128, 256, 384, 512)}
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.monotonic()
        with inference_precision('fp32'):
            for step in range(c['updates']):
                if time.monotonic()-tick > c['work_cap_seconds']:
                    raise TimeoutError('Decoder training work cap')
                bucket = (128, 256, 384, 512)[step % 4]
                batch = spec['batches'][str(bucket)]
                ident = str(order.choice(buckets[bucket]))
                names = order.choice(spec['conditions'], size=batch).tolist()
                context, target, features, keep, mask, coords = [x.cuda() for x in training_batch(data, ident, names)]
                noise = torch.randn(batch, 4*context.shape[1], 3, device='cuda', generator=rng) * model.scale_ref
                factor = min((step+1)/spec['warmup_updates'], 1) * (.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
                optimizer.param_groups[0]['lr'] = spec['learning_rate']*factor
                optimizer.zero_grad(set_to_none=True)
                loss, components = fragment_decoder_loss(model, context, target, features, keep, mask, coords, noise=noise)
                loss.backward()
                norm = torch.nn.utils.clip_grad_norm_(model.adapter.parameters(), 1., error_if_nonfinite=True)
                if not torch.isfinite(norm) or norm <= 0:
                    raise FloatingPointError('Invalid decoder adapter gradient')
                optimizer.step()
                with torch.no_grad():
                    for k, v in model.adapter.state_dict().items():
                        ema[k].lerp_(v, 1-spec['ema_decay'])
                m['updates'] = step+1
                m['training'].append(dict(step=step+1, bucket=bucket, length=context.shape[1], batch=batch,
                    target_id=ident, conditions=names, loss=float(loss.detach()), gradient_norm=float(norm),
                    position_mse=float(components['position_mse']), bond_mse=float(components['bond_mse']),
                    learning_rate_factor=factor, target_sha256=tensor_hash(target), context_sha256=tensor_hash(context), noise_sha256=tensor_hash(noise)))
                if step+1 == spec['profile_updates'] and not c['profile_only']:
                    torch.save(dict(raw={k: v.detach().cpu() for k, v in model.adapter.state_dict().items()},
                                    ema={k: v.cpu() for k, v in ema.items()}), a.output/'prefix_40.pt')
                    m['prefix_sha256'] = sha(a.output/'prefix_40.pt')
                if (step+1) % (10 if c['profile_only'] else 100) == 0:
                    atomic_json(a.output/'manifest.json', m)
                    print('update', step+1, 'loss', float(loss.detach()), flush=True)
                del context, target, features, keep, mask, coords, noise, loss, components
        torch.cuda.synchronize()
        m['training_seconds'] = time.monotonic()-start
        m['training_peak_reserved_GiB'] = torch.cuda.max_memory_reserved()/2**30
        m['final_adapter_sha256'] = state_hash(model.adapter.state_dict())
        if m['initial_adapter_sha256'] == m['final_adapter_sha256']:
            raise ValueError('Decoder adapter failed to update')
        torch.save(dict(raw={k: v.detach().cpu() for k, v in model.adapter.state_dict().items()},
                        ema={k: v.cpu() for k, v in ema.items()}, config=c), a.output/'checkpoint.pt')
        m['checkpoint_sha256'] = sha(a.output/'checkpoint.pt')
        model.adapter.load_state_dict(ema)
        model.eval()
        m['evaluated_adapter_sha256'] = state_hash(model.adapter.state_dict())
        start = time.monotonic()
        with torch.no_grad(), inference_precision('fp32'), h5py.File(c['baseline_predictions']) as old, \
                h5py.File(c['diagnostic_predictions']) as native, h5py.File(a.output/'initial_masked.h5') as initial, \
                h5py.File(a.output/'predictions.h5', 'x') as out:
            for r in selected:
                if time.monotonic()-tick > c['work_cap_seconds']:
                    raise TimeoutError('Decoder evaluation work cap')
                ident, item = r['id'], items[r['id']]
                features, keep, mask, coords, noise = evaluation_inputs(ident)
                contexts = dict(generated=torch.from_numpy(old['new/'+ident+'/latent'][:]).cuda(),
                                native=data[ident]['target'][None].expand(4, -1, -1).cuda())
                for kind, context in contexts.items():
                    arm = 'parent' if kind == 'generated' else 'native_direct'
                    bb = model(context, features, keep, mask, coords, noise=noise, drop_fragment=True, mask_fragment=False)
                    g = out.create_group(arm+'/'+ident)
                    g['latent'], g['backbone'] = context.cpu().numpy(), bb.cpu().numpy()
                    reference = old['new/'+ident+'/backbone'][:] if kind == 'generated' else native['native/'+ident+'/backbone'][:4]
                    check = check_backbones(bb.cpu().numpy(), reference, item['fragment'], item['start'], ident)
                    m['controls'].append(dict(kind=arm, target_id=ident, **check))
                    for dropped in (False, True):
                        arm = kind + ('_null' if dropped else '_cond')
                        torch.cuda.synchronize()
                        sample_start = time.monotonic()
                        bb = model(context, features, keep, mask, coords, noise=noise, drop_fragment=dropped)
                        torch.cuda.synchronize()
                        g = out.create_group(arm+'/'+ident)
                        g['latent'] = torch.where(keep[..., None], torch.zeros_like(context), context).cpu().numpy()
                        g['backbone'] = bb.cpu().numpy()
                        m['evaluations'].append(dict(arm=arm, target_id=ident, seconds=time.monotonic()-sample_start))
                        if dropped:
                            error = float(np.max(abs(bb.cpu().numpy()-initial[kind+'/'+ident+'/backbone'][:])))
                            if error > 1e-5:
                                raise ValueError('Condition-off output changed despite frozen decoder')
                            m['controls'].append(dict(kind=arm+'_initial', target_id=ident, backbone_max_abs=error))
                        else:
                            posed = (coords.double() @ coords.new_tensor([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64) + 11)*keep[..., None]
                            posed_bb = model(context, features, keep, mask, posed, noise=noise)
                            error = float((bb-posed_bb).abs().max())
                            if error > 1e-4:
                                raise ValueError('Decoder supplied-coordinate pose control failed')
                            g['pose_backbone'] = posed_bb.cpu().numpy()
                            m['controls'].append(dict(kind=arm+'_pose', target_id=ident, backbone_max_abs=error))
                            if ident == selected[0]['id']:
                                model.adapter.load_state_dict(initial_adapter(c))
                                saved = torch.load(a.output/'checkpoint.pt', map_location='cpu', weights_only=True)
                                model.adapter.load_state_dict(saved['ema'])
                                replay = model(context, features, keep, mask, coords, noise=noise)
                                error = float((replay-bb).abs().max())
                                if error > 1e-5:
                                    raise ValueError('Reset/reloaded decoder EMA differs')
                                g['reloaded_backbone'] = replay.cpu().numpy()
                                m['checkpoint_replay'].append(dict(arm=arm, target_id=ident, backbone_max_abs=error))
                out.flush()
                atomic_json(a.output/'manifest.json', m)
                print('evaluated', ident, flush=True)
        m['evaluation_seconds'] = time.monotonic()-start
        m['frozen_final'] = state_hash(canonical_frozen_state(model))
        m['peak_reserved_GiB'] = max(m['control_peak_reserved_GiB'], torch.cuda.max_memory_reserved()/2**30)
        if m['frozen_final'] != m['frozen_initial'] or m['peak_reserved_GiB'] > 75:
            raise ValueError('Changed frozen decoder or failed memory profile')
        m.update(status='complete', predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if telemetry:
            telemetry.close()
        m['elapsed_seconds'] = time.monotonic()-tick
        atomic_json(a.output/'manifest.json', m)


if __name__ == '__main__':
    main()
