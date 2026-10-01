"""Restore audited legacy state while keeping a new continuation protocol explicit."""
import torch


def clean_keys(values):
    result = {}
    for key, value in values.items():
        name = key.replace('_orig_mod.', '')
        if name in result:
            raise ValueError('colliding checkpoint names')
        result[name] = value
    return result


def validate_saved_state(model, saved):
    raw, ema = (clean_keys(saved[key]) for key in ('net', 'ema'))
    parameters = dict(model.named_parameters())
    if list(raw) != list(parameters) or list(ema) != list(parameters):
        raise ValueError('saved parameter ordering differs')
    groups = saved['opt']['param_groups']
    if len(groups) != 1:
        raise ValueError('expected one saved parameter group')
    ids = groups[0]['params']
    if len(ids) != len(parameters) or len(set(ids)) != len(ids) or set(ids) != set(saved['opt']['state']):
        raise ValueError('incomplete optimizer state')
    for (name, parameter), ident in zip(parameters.items(), ids):
        state = saved['opt']['state'][ident]
        for value in (raw[name], ema[name], state['exp_avg'], state['exp_avg_sq']):
            if value.shape != parameter.shape or not torch.isfinite(value).all():
                raise ValueError('invalid saved tensor '+name)
        if (state['exp_avg_sq'] < 0).any() or float(state['step']) != saved['step']:
            raise ValueError('invalid saved variance or update counter')
    return raw, ema


def restore_adam_state(optimizer, saved):
    """Restore moments and step counters, preserving the experiment's LR/kernel."""
    current = optimizer.state_dict()
    if len(current['param_groups']) != 1 or len(saved['param_groups']) != 1:
        raise ValueError('expected single optimizer groups')
    new, old = current['param_groups'][0], saved['param_groups'][0]
    for key in ('betas', 'eps', 'weight_decay', 'amsgrad', 'maximize'):
        if new[key] != old[key]:
            raise ValueError('incompatible saved optimizer '+key)
    if len(new['params']) != len(old['params']):
        raise ValueError('optimizer parameter count changed')
    states = {dest: {key: value.detach().clone() if isinstance(value, torch.Tensor) else value
                    for key, value in saved['state'][source].items()}
              for dest, source in zip(new['params'], old['params'])}
    optimizer.load_state_dict(dict(state=states, param_groups=current['param_groups']))
