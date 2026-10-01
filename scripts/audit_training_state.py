"""Inspect a trusted legacy training state without executing its training code."""
import argparse
import hashlib
import json
from pathlib import Path

import torch
from latentfold.pair_model import PairFlowNet


def clean_keys(values):
    out = {}
    for key, value in values.items():
        name = key.replace('_orig_mod.', '')
        if name in out:
            raise ValueError('compiled-key collision')
        out[name] = value
    return out


def audit(path, notes):
    state = torch.load(path, map_location='cpu', weights_only=False, mmap=True)
    raw, ema = (clean_keys(state[key]) for key in ('net', 'ema'))
    arch = dict(state['arch'], max_len=raw['pos.weight'].shape[0])
    extra = dict(state['extra_arch'])
    if extra.get('recycle') or extra.get('pair_contact') or extra.get('pair_dist_bins'):
        raise ValueError('unsupported architecture')
    for key in ('recycle', 'p_rec', 'rec_every'):
        extra.pop(key, None)
    with torch.device('meta'):
        model = PairFlowNet(**arch, **extra)
    parameters = dict(model.named_parameters())
    if list(raw) != list(ema) or list(parameters) != list(raw):
        raise ValueError('parameter/state ordering differs; positional optimizer restore unsafe')
    groups = state['opt']['param_groups']
    if len(groups) != 1 or len(groups[0]['params']) != len(parameters):
        raise ValueError('unexpected optimizer parameter groups')
    ids = groups[0]['params']
    if len(set(ids)) != len(ids) or set(ids) != set(state['opt']['state']):
        raise ValueError('optimizer state coverage differs')
    rows, steps = [], set()
    for (name, parameter), ident in zip(parameters.items(), ids):
        value, average = raw[name], ema[name]
        saved = state['opt']['state'][ident]
        if value.shape != parameter.shape or average.shape != value.shape:
            raise ValueError('parameter shape mismatch: '+name)
        for key in ('exp_avg', 'exp_avg_sq'):
            if saved[key].shape != value.shape or not torch.isfinite(saved[key]).all():
                raise ValueError('invalid optimizer moment: '+name)
        if not torch.isfinite(value).all() or not torch.isfinite(average).all():
            raise ValueError('nonfinite model state: '+name)
        if (saved['exp_avg_sq'] < 0).any():
            raise ValueError('negative optimizer variance: '+name)
        steps.add(int(saved['step']))
        difference = (value - average).double().square().sum().item()
        norm = average.double().square().sum().item()
        rows.append(dict(name=name, numel=value.numel(), raw_minus_ema_squared=difference,
                         ema_squared=norm, relative_l2=(difference / max(norm, 1e-30))**.5))
    if steps != {int(state['step'])}:
        raise ValueError('optimizer update counters do not match checkpoint step')
    group = {key: value for key, value in groups[0].items() if key != 'params'}
    result = dict(status='complete', checkpoint=str(path.resolve()), epoch=state['epoch'],
        step=state['step'], parameter_tensors=len(parameters), parameters=sum(p.numel() for p in parameters.values()),
        optimizer_order='State-dict parameter order exactly matches local named_parameters; one saved group with complete shape-matched moments.',
        optimizer_group=group, scheduler=state['sched'], source_training_config=notes['config'],
        saved_rng_keys=[key for key in state if 'rng' in key or key == 'gen'],
        exact_resume_possible=False,
        limitation='The legacy checkpoint saves CPU and data-order RNG only, not CUDA RNG or a fully specified original distributed data stream. Loading raw weights, EMA and optimizer is a state-restored continuation, not an exact replay.',
        raw_ema_relative_l2=(sum(r['raw_minus_ema_squared'] for r in rows)/sum(r['ema_squared'] for r in rows))**.5,
        parameters_audit=rows)
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            digest.update(block)
    result['checkpoint_sha256'] = digest.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--notes', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    result = audit(args.checkpoint, json.loads(args.notes.read_text()))
    args.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    group = result['optimizer_group']; config = result['source_training_config']
    text = ['# Original training-state audit', '',
        f"Checkpoint SHA256: `{result['checkpoint_sha256']}`. Epoch {result['epoch']}, update {result['step']}.", '',
        f"All {result['parameter_tensors']} parameter tensors ({result['parameters']:,} parameters) have finite raw weights, EMA weights, and shape-matched finite optimizer moments. Moment variances are nonnegative and every step counter agrees.", '',
        result['optimizer_order'], '',
        f"Original AdamW betas {group['betas']}; current learning rate {group['lr']}; original EMA decay {config['ema']}. The previous pilots used a fresh optimizer, EMA weights as their initialization, and EMA decay 0.99.", '',
        f"Relative L2 distance between original raw and EMA weights: {result['raw_ema_relative_l2']:.6f}.", '',
        result['limitation'], '',
        'A follow-up must isolate the effect of restoring optimizer moments from changing initial weights, loss reduction, learning rate, or data. Use identical raw initialization and frozen pilot settings for a fresh-versus-restored optimizer pair. Keep the original EMA as a separate starting state only when shared by both arms. Do not call this an exact training resume.']
    args.output.with_suffix('.md').write_text('\n'.join(text)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('parameters_audit','source_training_config','scheduler')}, indent=2))


if __name__ == '__main__':
    main()
