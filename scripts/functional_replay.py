"""Original-field replay on separate native-training families, without decoder use."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.flow import validate_batch
from prepare_overfit import sha


def state_digest(model):
    h=hashlib.sha256()
    for name,value in sorted(model.state_dict().items()):
        x=value.detach().cpu().contiguous();h.update(name.encode());h.update(str((x.dtype,tuple(x.shape))).encode());h.update(x.numpy().tobytes())
    return h.hexdigest()


def replay_loss(model,reference,z,esm,mask,*,generator):
    validate_batch(esm,mask,z)
    if reference.training or any(p.requires_grad for p in reference.parameters()):raise ValueError('replay reference must be frozen and eval')
    batch=len(z);noise=torch.randn(z.shape,device=z.device,generator=generator)
    t=torch.sigmoid(torch.randn(batch,device=z.device,generator=generator)).clamp(1e-4,1-1e-4)
    x=(1-t[:,None,None])*noise+t[:,None,None]*z
    drop=torch.rand(batch,device=z.device,generator=generator)<.1;use_sc=bool(torch.rand((),device=z.device,generator=generator)<.5)
    with torch.no_grad():
        pair=reference.compute_pair(esm,mask);sc=None
        if reference.self_cond and use_sc:sc=(x+(1-t[:,None,None])*reference(x,t,esm,mask,drop,None,pair=pair)).detach()
        target=reference(x,t,esm,mask,drop,sc,pair=pair).detach()
    actual=model(x,t,esm,mask,drop,sc,pair=model.compute_pair(esm,mask))
    error=(actual-target).square().mean(-1);loss=((error*mask).sum(1)/mask.sum(1)).mean()
    if not torch.isfinite(loss):raise FloatingPointError('nonfinite functional replay')
    return loss,dict(replay_loss=float(loss.detach()),max_velocity_error=float((actual.detach()-target).abs()[mask].max()),self_conditioned=use_sc,dropped=int(drop.sum()))


def controlled_replay_backward(model,primary,make_replay,*,weight,max_ratio):
    """Free primary activations before constructing the independent replay graph."""
    parameters=[p for p in model.parameters() if p.requires_grad]
    primary_grads=torch.autograd.grad(primary,parameters,allow_unused=True)
    def norm(values):
        value=torch.stack([g.square().sum(dtype=torch.float64) for g in values if g is not None]).sum().sqrt()
        if not torch.isfinite(value):raise FloatingPointError('nonfinite replay-combination gradient')
        return float(value)
    primary_norm=norm(primary_grads)
    replay,stats=make_replay();aux_grads=torch.autograd.grad(replay,parameters,allow_unused=True);aux_norm=norm(aux_grads)
    effective=min(weight,max_ratio*primary_norm/(aux_norm+1e-30))
    for parameter,left,right in zip(parameters,primary_grads,aux_grads):
        if left is None:parameter.grad=None if right is None else right.mul_(effective)
        else:
            if right is not None:left.add_(right,alpha=effective)
            parameter.grad=left
    stats.update(primary_gradient_norm=primary_norm,replay_gradient_norm=aux_norm,effective_weight=effective,replay_to_primary_ratio=effective*aux_norm/(primary_norm+1e-30))
    return stats


class ReplayBank:
    def __init__(self,c,training_records):
        for key in ('replay_protocol','replay_selection'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
        self.protocol=json.loads(Path(c['replay_protocol']).read_text());selection=json.loads(Path(c['replay_selection']).read_text());self.recipe=self.protocol['replay']
        base=json.loads(Path(c['protocol']).read_text())
        if c['seed'] not in self.protocol['seeds'] or c['updates']!=(40 if c['profile_only'] else 2000):raise ValueError('wrong replay training budget/seed')
        for key in ('learning_rate','warmup_updates','ema_decay','batches','evaluation_guidance','evaluation_seed'):
            if c[key]!=base[key]:raise ValueError('replay changes primary '+key)
        for key in ('native_selection','corpus_inventory','embedding_cache'):
            if sha(selection[key])!=selection[key+'_sha256']:raise ValueError('changed replay '+key)
        native=json.loads(Path(selection['native_selection']).read_text());used={r['family'] for r in training_records.values()};rows=[r for r in native['train'] if r['family'] not in used]
        if len(rows)!=390 or len({r['family'] for r in rows})!=390 or rows!=selection['targets']:raise ValueError('replay family selection differs')
        self.records={};self.buckets={b:[] for b in (128,256,384,512)}
        with h5py.File(native['dataset']) as source,h5py.File(selection['embedding_cache']) as cache:
            for r in rows:
                ident=r['id'];g=source['train'][ident];e=cache['train'][ident];z=g['z'][:];esm=e['80'][:]
                if hashlib.sha256(z.tobytes()).hexdigest()!=r['array_sha256']['z'] or e.attrs['sequence_sha256']!=r['sequence_sha256'] or esm.shape!=(r['length'],2560) or not np.isfinite(esm).all() or not np.isfinite(z).all():raise ValueError('replay arrays changed')
                self.records[ident]=dict(r,z=torch.from_numpy(z),esm=torch.from_numpy(esm));self.buckets[r['bucket']].append(ident)
        self.reset(c['seed'])

    def reset(self,seed):
        self.queues={b:[] for b in self.buckets};self.order=np.random.default_rng(seed+self.recipe['order_offset'])
        self.generator=torch.Generator(device='cuda').manual_seed(seed+self.recipe['rng_offset'])

    def batch(self,step):
        length=sorted(self.buckets)[step%4];count=self.recipe['batch']
        while len(self.queues[length])<count:self.queues[length].extend(self.order.permutation(self.buckets[length]).tolist())
        ids=self.queues[length][:count];del self.queues[length][:count]
        z=torch.zeros(count,length,8,device='cuda');esm=torch.zeros(count,length,2560,device='cuda');mask=torch.zeros(count,length,device='cuda',dtype=torch.bool)
        for i,ident in enumerate(ids):
            r=self.records[ident];n=r['length'];z[i,:n]=r['z'].cuda();esm[i,:n]=r['esm'].cuda();mask[i,:n]=True
        return ids,z,esm,mask
