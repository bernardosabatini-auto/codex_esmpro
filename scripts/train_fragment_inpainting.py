"""Train a conditional coordinate flow with supplied motif atoms fixed in its state."""
import argparse
import json
import math
import time
from pathlib import Path

import h5py
import numpy as np
import torch

from latentfold.decoder import load_proteinae
from latentfold.fragment_decoder_fm import sample_times
from latentfold.fragment_inpainting import FragmentInpaintingDecoder, inpainting_loss, place_fragment, context_mask
from latentfold.fragment_decoder import FragmentDecoder
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from extra_fragment_validation_core import load_conditions
from evaluate_decoder_fragment_variance import check_backbones
from fragment_inpainting_core import (audit, load_training, training_batch, panel,
    canonical_frozen_state, expected_frozen_state, initial_adapter, initial_model_state)
from native_anchor_training_core import state_hash, tensor_hash
from prepare_overfit import sha
from profile_gpu import Telemetry, atomic_json


def main():
    p = argparse.ArgumentParser()
    for name in ('source', 'config', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    c = json.loads(a.config.read_text())
    if 'flank_protocol' in c:
        from fragment_flank_core import audit_worker
        spec = audit_worker(c)
        data = torch.load(c['flank_training_cache'], map_location='cpu', weights_only=True)
    else:
        spec = audit(c)
        data = load_training(c)
    loss_options = c.get('junction_loss', {})
    selected = panel(c)
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
        codec = load_proteinae(a.source/'ProteinAE_v1', Path(c['decoder_checkpoint']), steps=3).cuda().eval()
        model = FragmentInpaintingDecoder(codec, seed=spec['seed'], context_flank=c.get('context_flank', 0)).cuda().eval()
        m['frozen_original'] = state_hash(expected_frozen_state(c))
        m['frozen_initial'] = state_hash(canonical_frozen_state(model))
        m['initial_model_sha256'] = state_hash(model.state_dict())
        if m['frozen_original'] != m['frozen_initial'] or m['initial_model_sha256'] != state_hash(initial_model_state(c)):
            raise ValueError('Changed pretrained decoder or zero adapter initialization')
        m['trainable_parameters'] = sum(p.numel() for p in model.parameters() if p.requires_grad)
        if not all(p.requires_grad for p in model.parameters()) or any(p.requires_grad for p in codec.parameters()):
            raise ValueError('Private decoder must train; original codec must stay frozen')
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
                    hidden = context_mask(keep, model.context_flank)
                    z = torch.where(hidden[..., None], torch.zeros_like(context), context)
                    expected = codec(z, mask, noise=noise, return_backbone=True)[1]
                    bb = FragmentDecoder.forward(model, z, features, keep, mask, coords, noise=noise)
                    error = float((bb-expected).abs().max())
                    if error > 1e-5:
                        raise ValueError('Zero decoder adapter changed masked decoding')
                    g = initial.create_group(kind+'/'+ident)
                    g['latent'], g['backbone'], g['original_backbone'] = z.cpu().numpy(), bb.cpu().numpy(), expected.cpu().numpy()
                    reference = old['new/'+ident+'/backbone'][:] if kind == 'generated' else native['native/'+ident+'/backbone'][:4]
                    anchors = place_fragment(torch.from_numpy(item['fragment']).cuda(),torch.from_numpy(reference).cuda(),item['start'])
                    clamped = model(context,features,keep,mask,coords,anchors=anchors,noise=noise)
                    g['anchors'],g['clamped_backbone']=anchors.cpu().numpy(),clamped.cpu().numpy()
                    if 'flank_protocol' in c:
                        g['source_latent'] = context.cpu().numpy()
                        if ident in initial_ids:
                            model.context_flank = 0
                            zero = model(context,features,keep,mask,coords,anchors=anchors,noise=noise)
                            model.context_flank = c['context_flank']
                            with h5py.File(c['flank_baseline_predictions']) as baseline:
                                expected_zero = torch.from_numpy(baseline[kind+'_untrained/'+ident+'/backbone'][:]).cuda()
                            error_zero = float((zero-expected_zero).abs().max())
                            g['zero_width_backbone'] = zero.cpu().numpy()
                            m.setdefault('flank_controls', []).append(dict(kind='zero_width', arm=kind, target_id=ident, max_abs=error_zero))
                            if error_zero > 1e-5: raise ValueError('Zero-width historical untrained replay changed')
                    m['initial_controls'].append(dict(kind=kind+'_masked', target_id=ident, backbone_max_abs=error))
                    if ident in initial_ids:
                        expected = codec(context, mask, noise=noise, return_backbone=True)[1]
                        bb = FragmentDecoder.forward(model, context, features, keep, mask, coords, noise=noise, mask_fragment=False)
                        error = float((bb-expected).abs().max())
                        if error > 1e-5:
                            raise ValueError('Zero decoder adapter changed original decoding')
                        reference = old['new/'+ident+'/backbone'][:] if kind == 'generated' else native['native/'+ident+'/backbone'][:4]
                        check = check_backbones(bb.cpu().numpy(), reference, item['fragment'], item['start'], ident)
                        g = clean.create_group(kind+'/'+ident)
                        g['backbone'], g['original_backbone'] = bb.cpu().numpy(), expected.cpu().numpy()
                        m['initial_controls'].append(dict(kind=kind+'_clean', target_id=ident, backbone_max_abs=error, **check))
                        if kind == 'native':
                            from latentfold.metrics import ca_metrics
                            pred=bb[0,:,1].cpu().numpy(); target_ca=data[ident]['backbone'][:,1].numpy()
                            centered=float(np.sqrt(np.mean(np.sum(((pred-pred.mean(0))-(target_ca-target_ca.mean(0)))**2,-1))))
                            proper=ca_metrics(pred,target_ca)['ca_rmsd']
                            if centered > proper+.1: raise ValueError('Native code/target pose mismatch')
                            m.setdefault('frame_controls',[]).append(dict(target_id=ident,centered_ca_rmsd=centered,proper_ca_rmsd=proper))
        m['initial_masked_sha256'], m['initial_clean_sha256'] = sha(a.output/'initial_masked.h5'), sha(a.output/'initial_clean.h5')

        # Validate checkpointing through the real external decoder at initialization.
        ident = initial_ids[0]
        values = [x.cuda() for x in training_batch(data, ident, ['c20_center'])]
        context, target, features, keep, mask, coords = values
        noise = evaluation_inputs(ident)[-1][:1]
        grads, predictions, losses = [], [], []
        model.train()
        with inference_precision('fp32'):
            for checkpointed in (False, True):
                model.zero_grad(set_to_none=True)
                loss, _, bb = inpainting_loss(model, context, target, features, keep, mask, coords, noise=noise, t=noise.new_full((1,),.4), dropped=torch.zeros(1,dtype=torch.bool,device='cuda'), checkpointed=checkpointed, **loss_options)
                loss.backward()
                predictions.append(bb.detach())
                losses.append(float(loss.detach()))
                grads.append({k: p.grad.detach().clone() for k, p in model.named_parameters() if p.grad is not None})
            error = max(float((grads[0][k]-grads[1][k]).abs().max()) for k in grads[0])
            if (not torch.allclose(predictions[0], predictions[1], atol=1e-4, rtol=1e-4)
                    or any(not torch.allclose(grads[0][k], grads[1][k], atol=1e-4, rtol=1e-4) for k in grads[0])
                    or not math.isclose(losses[0], losses[1], abs_tol=1e-4, rel_tol=1e-4)
                    or any(p.grad is not None for p in codec.parameters())
                    or set(grads[0]) != set(grads[1])
                    or not any(k.startswith('decoder.') and v.norm()>0 for k,v in grads[1].items())
                    or grads[1]['adapter.output.weight'].norm() <= 0 or grads[1]['adapter.pair_output.weight'].norm() <= 0):
                raise ValueError('Actual decoder gradient/checkpoint control failed')
            m['gradient_control'] = dict(target_id=ident, decoder_gradient_norm=float(torch.stack([v.square().sum() for k,v in grads[1].items() if k.startswith('decoder.')]).sum().sqrt()), gradient_parameters=len(grads[1]), prediction_max_abs=float((predictions[0]-predictions[1]).abs().max()),
                gradient_max_abs=error, losses=losses, token_gradient_norm=float(grads[1]['adapter.output.weight'].norm()),
                pair_gradient_norm=float(grads[1]['adapter.pair_output.weight'].norm()),
                prediction_tolerance_ratio=float(((predictions[0]-predictions[1]).abs()/(1e-4+1e-4*predictions[1].abs())).max()),
                gradient_tolerance_ratio=max(float(((grads[0][k]-grads[1][k]).abs()/(1e-4+1e-4*grads[1][k].abs())).max()) for k in grads[0]))
        del grads, predictions, values, context, target, features, keep, mask, coords, noise, loss, bb
        model.zero_grad(set_to_none=True)
        m['control_peak_reserved_GiB'] = torch.cuda.max_memory_reserved()/2**30
        atomic_json(a.output/'manifest.json', m)

        optimizer = torch.optim.AdamW([dict(params=model.decoder.parameters(),lr=spec['decoder_learning_rate']),dict(params=model.adapter.parameters(),lr=spec['adapter_learning_rate'])], betas=(.9, .95), weight_decay=.01, foreach=False)
        ema = {k: v.detach().clone() for k, v in model.state_dict().items()}
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
                times=sample_times(batch,generator=rng,device='cuda')
                dropped=torch.rand(batch,generator=rng,device='cuda') < spec['condition_dropout']
                factor = min((step+1)/spec['warmup_updates'], 1) * (.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
                optimizer.param_groups[0]['lr'] = spec['decoder_learning_rate']*factor
                optimizer.param_groups[1]['lr'] = spec['adapter_learning_rate']*factor
                optimizer.zero_grad(set_to_none=True)
                loss, components, predicted = inpainting_loss(model, context, target, features, keep, mask, coords, noise=noise, t=times, dropped=dropped, **loss_options)
                loss.backward()
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True)
                if not torch.isfinite(norm) or norm <= 0:
                    raise FloatingPointError('Invalid decoder adapter gradient')
                optimizer.step()
                with torch.no_grad():
                    for k, v in model.state_dict().items():
                        ema[k].lerp_(v, 1-spec['ema_decay'])
                m['updates'] = step+1
                m['training'].append(dict(step=step+1, bucket=bucket, length=context.shape[1], batch=batch,
                    target_id=ident, conditions=names, loss=float(loss.detach()), gradient_norm=float(norm),
                    unknown_fm=float(components['unknown_fm']),
                    times=times.tolist(), dropped=dropped.tolist(), time_sha256=tensor_hash(times), dropout_sha256=tensor_hash(dropped),
                    learning_rate_factor=factor, target_sha256=tensor_hash(target), context_sha256=tensor_hash(context), noise_sha256=tensor_hash(noise)))
                if step+1 == spec['profile_updates'] and not c['profile_only']:
                    torch.save(dict(raw={k: v.detach().cpu() for k, v in model.state_dict().items()},
                                    ema={k: v.cpu() for k, v in ema.items()}), a.output/'prefix_40.pt')
                    m['prefix_sha256'] = sha(a.output/'prefix_40.pt')
                if (step+1) % (10 if c['profile_only'] else 100) == 0:
                    atomic_json(a.output/'manifest.json', m)
                    print('update', step+1, 'loss', float(loss.detach()), flush=True)
                del context, target, features, keep, mask, coords, noise, loss, components, predicted, times, dropped
        torch.cuda.synchronize()
        m['training_seconds'] = time.monotonic()-start
        m['training_peak_reserved_GiB'] = torch.cuda.max_memory_reserved()/2**30
        m['final_model_sha256'] = state_hash(model.state_dict())
        if m['initial_model_sha256'] == m['final_model_sha256']:
            raise ValueError('Decoder adapter failed to update')
        torch.save(dict(raw={k: v.detach().cpu() for k, v in model.state_dict().items()},
                        ema={k: v.cpu() for k, v in ema.items()}, config=c), a.output/'checkpoint.pt')
        m['checkpoint_sha256'] = sha(a.output/'checkpoint.pt')
        saved = torch.load(a.output/'checkpoint.pt', map_location='cpu', weights_only=True)
        model.load_state_dict(saved['ema'])
        del saved
        model.eval()
        m['evaluated_model_sha256'] = state_hash(model.state_dict())
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
                    bb = codec(context,mask,noise=noise,return_backbone=True)[1]
                    g = out.create_group(arm+'/'+ident)
                    g['latent'], g['backbone'] = context.cpu().numpy(), bb.cpu().numpy()
                    reference = old['new/'+ident+'/backbone'][:] if kind == 'generated' else native['native/'+ident+'/backbone'][:4]
                    check = check_backbones(bb.cpu().numpy(), reference, item['fragment'], item['start'], ident)
                    m['controls'].append(dict(kind=arm, target_id=ident, **check))
                    anchors = place_fragment(torch.from_numpy(item['fragment']).cuda(),torch.from_numpy(reference).cuda(),item['start'])
                    g=out.create_group(kind+'_untrained/'+ident)
                    g['latent']=initial[kind+'/'+ident+'/latent'][:]
                    g['backbone']=initial[kind+'/'+ident+'/clamped_backbone'][:]
                    for dropped in (False, True):
                        arm = kind + ('_null' if dropped else '_cond')
                        torch.cuda.synchronize()
                        sample_start = time.monotonic()
                        bb = model(context, features, keep, mask, coords, anchors=anchors, noise=noise, drop_fragment=dropped)
                        torch.cuda.synchronize()
                        g = out.create_group(arm+'/'+ident)
                        g['latent'] = torch.where(context_mask(keep, model.context_flank)[..., None], torch.zeros_like(context), context).cpu().numpy()
                        if 'flank_protocol' in c: g['source_latent'] = context.cpu().numpy()
                        g['backbone'] = bb.cpu().numpy()
                        m['evaluations'].append(dict(arm=arm, target_id=ident, seconds=time.monotonic()-sample_start))
                        if dropped:
                            hidden=context.clone();hidden[context_mask(keep, model.context_flank)]+=97
                            altered=features.clone();altered[...,:28]+=keep[...,None]*13
                            repeat = model(hidden,altered,keep,mask,coords+keep[...,None]*17,anchors=anchors+keep[...,None,None]*19,noise=noise,drop_fragment=True)
                            error = float((bb-repeat).abs().max())
                            if error > 1e-5: raise ValueError('Adapted null repeat changed')
                            g['repeat_backbone']=repeat.cpu().numpy()
                            m['controls'].append(dict(kind=arm+'_repeat', target_id=ident, backbone_max_abs=error))
                        else:
                            posed = (coords.double() @ coords.new_tensor([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64) + 11)*keep[..., None]
                            fragment=torch.from_numpy(item['fragment']).cuda().double()
                            fragment=fragment@coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11
                            posed_anchors=place_fragment(fragment,torch.from_numpy(reference).cuda(),item['start'])
                            posed_bb = model(context, features, keep, mask, posed, anchors=posed_anchors, noise=noise)
                            error = float((bb-posed_bb).abs().max())
                            if error > 1e-4:
                                raise ValueError('Decoder supplied-coordinate pose control failed')
                            g['pose_backbone'] = posed_bb.cpu().numpy()
                            if 'flank_protocol' in c and ident in initial_ids:
                                hidden = context.clone(); hidden[context_mask(keep, model.context_flank)] += 97
                                eps = noise.clone(); eps[keep.repeat_interleave(4, 1)] += 111
                                repeat = model(hidden,features,keep,mask,coords,anchors=anchors,noise=eps)
                                error_hidden = float((repeat-bb).abs().max())
                                g['nonleak_backbone'] = repeat.cpu().numpy()
                                m['flank_controls'].append(dict(kind='nonleak',arm=kind,target_id=ident,max_abs=error_hidden))
                                if error_hidden > 1e-5: raise ValueError('Hidden flank codes or fixed-atom noise leaked')
                            m['controls'].append(dict(kind=arm+'_pose', target_id=ident, backbone_max_abs=error))
                            if ident == selected[0]['id']:
                                model.load_state_dict(initial_model_state(c))
                                saved = torch.load(a.output/'checkpoint.pt', map_location='cpu', weights_only=True)
                                model.load_state_dict(saved['ema'])
                                replay = model(context, features, keep, mask, coords, anchors=anchors, noise=noise)
                                error = float((replay-bb).abs().max())
                                if error > 1e-5:
                                    raise ValueError('Reset/reloaded decoder EMA differs')
                                g['reloaded_backbone'] = replay.cpu().numpy()
                                m['checkpoint_replay'].append(dict(arm=arm, target_id=ident, backbone_max_abs=error))
                out.flush()
                atomic_json(a.output/'manifest.json', m)
                print('evaluated', ident, flush=True)
        m['evaluation_seconds'] = time.monotonic()-start
        m['frozen_final'] = state_hash(codec.decoder.state_dict())
        m['adapted_decoder_final'] = state_hash(canonical_frozen_state(model))
        m['peak_reserved_GiB'] = max(m['control_peak_reserved_GiB'], torch.cuda.max_memory_reserved()/2**30)
        if m['frozen_final'] != m['frozen_initial'] or m['adapted_decoder_final'] == m['frozen_initial'] or m['peak_reserved_GiB'] > 75:
            raise ValueError('Changed frozen decoder or failed memory profile')
        if 'flank_protocol' in c: audit_worker(c)
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
