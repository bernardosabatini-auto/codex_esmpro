"""Length-bucketed FP32 codec calls with per-protein deterministic decoder noise."""
import math,time
import numpy as np
import torch
from torch.nn import functional as F
from .backbone import encode_backbone
from .flow import target_noise


def pack_backbones(items,device):
    if not items:raise ValueError('Empty codec batch')
    lengths=[len(r['backbone']) for r in items];width=32*math.ceil(max(lengths)/32)
    x=torch.zeros(len(items),width,4,3,dtype=torch.float32,device=device);mask=torch.arange(width,device=device)[None]<torch.tensor(lengths,device=device)[:,None]
    for i,r in enumerate(items):
        value=np.asarray(r['backbone'])
        if value.shape!=(lengths[i],4,3) or lengths[i]<1 or not np.isfinite(value).all():raise ValueError('Invalid complete codec backbone')
        x[i,:lengths[i]]=torch.as_tensor(value,dtype=torch.float32,device=device)
    return x,mask,lengths


@torch.no_grad()
def run_codec_batches(decoder,items,*,batch_size,seed):
    keys=[r['key'] for r in items]
    if len(set(keys))!=len(keys) or batch_size<1:raise ValueError('Duplicated codec item or invalid batch')
    buckets={}
    for item in items:buckets.setdefault(32*math.ceil(len(item['backbone'])/32),[]).append(item)
    results={};batches=[]
    for width,group in sorted(buckets.items()):
        for start in range(0,len(group),batch_size):
            chunk=group[start:start+batch_size];torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();x,mask,lengths=pack_backbones(chunk,'cuda');encoded=encode_backbone(decoder,x,mask);z=F.layer_norm(encoded,(8,));noise=torch.zeros(len(chunk),4*width,3,device='cuda')
            for i,r in enumerate(chunk):
                n=lengths[i]
                if r.get('reference_latent') is not None:
                    value=np.asarray(r['reference_latent'])
                    if value.shape!=(n,8) or not np.isfinite(value).all():raise ValueError('Invalid cached full target')
                    z[i,:n]=torch.as_tensor(value,device='cuda')
                noise[i,:4*n]=target_noise([r['target_id']],[4*n],3,seed=seed,stream=r['stream'],device='cuda')[0]*decoder.fm.scale_ref
            _,backbone=decoder(z,mask,noise=noise,return_backbone=True);encoded,z,backbone=[v.cpu().numpy() for v in (encoded,z,backbone)];torch.cuda.synchronize();batches.append(dict(width=width,items=len(chunk),seconds=time.monotonic()-tick,peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30))
            for i,r in enumerate(chunk):
                n=lengths[i];results[r['key']]=dict(encoded=encoded[i,:n].copy(),latent=z[i,:n].copy(),backbone=backbone[i,:n].copy())
    return results,batches
