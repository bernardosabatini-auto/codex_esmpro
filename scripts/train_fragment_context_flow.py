"""Paired, small contextual-code flows; never load the scaffold generator."""
import argparse
import copy
import hashlib
import json
import math
import time
from pathlib import Path
import numpy as np
import torch
from latentfold.fragment_context_flow import ContextFlow, sample_codes
from prepare_overfit import sha
from profile_gpu import Telemetry, atomic_json


def digest(values):
    h = hashlib.sha256()
    for key, value in sorted(values.items()):
        h.update(key.encode()); h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def load_data(c):
    if sha(c['data_manifest']) != c['data_manifest_sha256']:
        raise ValueError('Changed export manifest')
    m = json.loads(Path(c['data_manifest']).read_text()); spec = m['spec']
    if m['status'] != 'complete' or not m['no_evaluation_targets'] or sha(m['arrays']) != m['arrays_sha256']:
        raise ValueError('Changed or incomplete export')
    a = dict(np.load(m['arrays'], allow_pickle=False))
    expected = {s+'_'+k for s in ('train', 'validation', 'evaluation') for k in ('features', 'placement')}
    expected |= {'train_targets', 'validation_targets', 'mean', 'std'}
    if set(a) != expected or c['updates'] != spec['profile_updates' if c['profile_only'] else 'updates']:
        raise ValueError('Wrong data inventory or update budget')
    if any(not np.isfinite(x).all() for x in a.values()):
        raise ValueError('Nonfinite arrays')
    return m, {k: torch.from_numpy(v.copy()).float() for k, v in a.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); c = json.loads(a.config.read_text()); data, cpu = load_data(c); spec = data['spec']
    a.output.mkdir(exist_ok=False); start = time.monotonic(); telemetry = None
    m = dict(status='running', config=c, arms={}, controls=[], data_manifest_sha256=c['data_manifest_sha256'])
    atomic_json(a.output/'manifest.json', m)
    try:
        torch.set_num_threads(2); torch.cuda.set_device(0); torch.cuda.set_per_process_memory_fraction(.85)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        # Explicit math attention avoids train/eval fast-path changes in prefix replay.
        torch.backends.mha.set_fastpath_enabled(False)
        torch.backends.cuda.enable_flash_sdp(False); torch.backends.cuda.enable_mem_efficient_sdp(False)
        telemetry = Telemetry(a.output, True)
        d = {k: v.cuda() for k, v in cpu.items()}
        d['train_targets'] = (d['train_targets']-d['mean'])/d['std']
        d['validation_targets'] = (d['validation_targets']-d['mean'])/d['std']
        vrng = torch.Generator().manual_seed(spec['seed']+2)
        vn = torch.randn(cpu['validation_targets'].shape, generator=vrng).cuda()
        vt = torch.rand(len(vn), generator=vrng).cuda()
        vx = (1-vt[:, None, None])*vn+vt[:, None, None]*d['validation_targets']
        vtarget = d['validation_targets']-vn
        initial_hash = None; first_predictions = None; matched_draws = None
        for arm in spec['arms']:
            torch.manual_seed(spec['seed']); torch.cuda.manual_seed_all(spec['seed'])
            model = ContextFlow(**spec['architecture']).cuda(); ema = copy.deepcopy(model).eval().requires_grad_(False)
            ih = digest(model.state_dict())
            if initial_hash is not None and ih != initial_hash:
                raise ValueError('Initial weights differ')
            initial_hash = ih
            features = d['train_features'] if arm == 'isolated' else torch.zeros_like(d['train_features'])
            vf = d['validation_features'] if arm == 'isolated' else torch.zeros_like(d['validation_features'])
            with torch.no_grad():
                initial = model(vx, vt, vf, d['validation_placement']).cpu()
            if first_predictions is not None and not torch.equal(first_predictions, initial):
                raise ValueError('Initial predictions differ')
            first_predictions = initial
            optimizer = torch.optim.AdamW(model.parameters(), lr=spec['learning_rate'],
                                         betas=tuple(spec['optimizer']['betas']), weight_decay=spec['optimizer']['weight_decay'])
            rng = torch.Generator().manual_seed(spec['seed']+1)
            draws = []; losses = []; max_condition_gradient = 0.
            torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); tick = time.monotonic()
            for step in range(1, c['updates']+1):
                if time.monotonic()-start > c['work_cap_seconds']:
                    raise TimeoutError('Context flow work cap')
                ids = torch.randint(len(features), (spec['batch'],), generator=rng)
                noise = torch.randn(spec['batch'], 20, 8, generator=rng)
                times = torch.rand(spec['batch'], generator=rng)
                draws.append(digest(dict(ids=ids, noise=noise, times=times)))
                ids = ids.cuda(); noise = noise.cuda(); times = times.cuda()
                target = d['train_targets'][ids]
                x = (1-times[:, None, None])*noise+times[:, None, None]*target
                factor = min(step/spec['warmup_updates'], 1.)*(spec['lr_floor']+(1-spec['lr_floor'])*.5*(1+math.cos(math.pi*step/spec['updates'])))
                optimizer.param_groups[0]['lr'] = spec['learning_rate']*factor
                optimizer.zero_grad(set_to_none=True)
                velocity = model(x, times, features[ids], d['train_placement'][ids])
                loss = (velocity-(target-noise)).square().mean()
                loss.backward()
                gradient = torch.nn.utils.clip_grad_norm_(model.parameters(), spec['gradient_clip'], error_if_nonfinite=True)
                cg = float(model.condition.weight.grad.norm())
                max_condition_gradient = max(max_condition_gradient, cg)
                if not torch.isfinite(loss) or not torch.isfinite(gradient):
                    raise ValueError('Nonfinite training')
                optimizer.step()
                with torch.no_grad():
                    for ep, mp in zip(ema.parameters(), model.parameters()):
                        ep.mul_(spec['ema']).add_(mp, alpha=1-spec['ema'])
                losses.append(float(loss.detach()))
                if step == spec['profile_updates']:
                    prefix = dict(raw=digest(model.state_dict()), ema=digest(ema.state_dict()), draws=draws.copy())
                if step % 200 == 0:
                    print(arm, step, losses[-1], flush=True)
            torch.cuda.synchronize(); seconds = time.monotonic()-tick
            if matched_draws is not None and draws != matched_draws:
                raise ValueError('Paired draws differ')
            matched_draws = draws
            if (arm == 'isolated' and max_condition_gradient <= 0) or (arm == 'ablated' and max_condition_gradient != 0):
                raise ValueError('Wrong conditioning gradient route')
            with torch.no_grad():
                prediction = ema(vx, vt, vf, d['validation_placement'])
                validation_loss = (prediction-vtarget).square().mean((1, 2)).cpu().tolist()
                permuted = ema(vx, vt, vf.flip(0), d['validation_placement'])
                sensitivity = float((prediction-permuted).abs().max())
            if (arm == 'isolated' and sensitivity <= 0) or (arm == 'ablated' and sensitivity != 0):
                raise ValueError('Wrong conditioning sensitivity')
            path = a.output/(arm+'.pt')
            torch.save(dict(model=model.state_dict(), ema=ema.state_dict(), spec=spec,
                            mean=cpu['mean'], std=cpu['std'], data_manifest_sha256=c['data_manifest_sha256']), path)
            reload = ContextFlow(**spec['architecture']).cuda().eval()
            reload.load_state_dict(torch.load(path, weights_only=True)['ema'])
            with torch.no_grad():
                if not torch.equal(prediction, reload(vx, vt, vf, d['validation_placement'])):
                    raise ValueError('EMA reload mismatch')
                # Sample both models with identical code noise; no native evaluation targets exist here.
                erng = torch.Generator().manual_seed(spec['seed']+3)
                en = torch.randn(32, 4, 20, 8, generator=erng).reshape(128, 20, 8).cuda()
                ef = d['evaluation_features'].repeat_interleave(4, 0)
                if arm == 'ablated': ef = torch.zeros_like(ef)
                ep = d['evaluation_placement'].repeat_interleave(4, 0)
                codes = sample_codes(ema, en, ef, ep)*d['std']+d['mean']
                np.save(a.output/(arm+'_codes.npy'), codes.cpu().numpy())
            if not c['profile_only']:
                report = json.loads(Path(c['profile_report']).read_text())
                if sha(c['profile_report']) != c['profile_report_sha256'] or not report['qualified']:
                    raise ValueError('Changed/failed technical profile')
                if prefix != report['arms'][arm]['prefix']:
                    raise ValueError('Profile prefix replay differs')
            m['arms'][arm] = dict(initial_hash=ih, prefix=prefix, draws=draws, losses=losses,
                training_seconds=seconds, peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30,
                max_condition_gradient=max_condition_gradient, validation_loss=validation_loss,
                initial_validation_loss=(initial-vtarget.cpu()).square().mean((1, 2)).tolist(),
                sensitivity=sensitivity, reload_exact=True, checkpoint_sha256=sha(path),
                codes_sha256=sha(a.output/(arm+'_codes.npy')), parameters=sum(p.numel() for p in model.parameters()))
            atomic_json(a.output/'manifest.json', m)
            del model, ema, reload, optimizer; torch.cuda.empty_cache()
        m['status'] = 'complete'
    except BaseException as error:
        m.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if telemetry: telemetry.close()
        m['elapsed_seconds'] = time.monotonic()-start
        atomic_json(a.output/'manifest.json', m)


if __name__ == '__main__':
    main()
