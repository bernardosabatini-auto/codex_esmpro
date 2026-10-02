"""Strict FP32 interpolation between checkpoints sharing one initialization."""
import math
import torch


def clean_state(state):
    out={}
    for name,value in state.items():
        key=name.replace('_orig_mod.','')
        if key in out:raise ValueError('colliding checkpoint keys')
        out[key]=value
    return out


@torch.no_grad()
def blend_states(initial,trained,alpha):
    if isinstance(alpha,bool) or not math.isfinite(alpha) or not 0<=alpha<=1:raise ValueError('invalid blend weight')
    initial,trained=clean_state(initial),clean_state(trained)
    if set(initial)!=set(trained):raise ValueError('checkpoint keys differ')
    out={}
    for key,a in initial.items():
        b=trained[key]
        if a.shape!=b.shape or a.dtype!=b.dtype:raise ValueError('checkpoint shape or dtype differs')
        if a.is_floating_point():
            if a.dtype!=torch.float32 or not torch.isfinite(a).all() or not torch.isfinite(b).all():raise ValueError('expected finite FP32 weights')
            out[key]=torch.lerp(a,b,alpha)
        else:
            if not torch.equal(a,b):raise ValueError('nonfloating state differs')
            out[key]=a.clone()
    return out


def architecture(payload):
    weights=clean_state(payload['ema']);arch=dict(payload['arch']);arch['max_len']=weights['pos.weight'].shape[0]
    extra=dict(payload.get('extra_arch') or {})
    if extra.get('recycle'):raise ValueError('unsupported recycling')
    for k in ('recycle','p_rec','rec_every'):extra.pop(k,None)
    return dict(arch=arch,extra_arch=extra,model=payload['model'])
