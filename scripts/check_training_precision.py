"""Four bounded actual-weight gradient checks before confidence-weighted training."""
import gc
import torch
from torch.nn import functional as F
from latentfold.data import collate
from latentfold.flow import FlowConfig
from latentfold.training import objective
from latentfold.precision import inference_precision


def check(model, decoder, records, buckets):
    rng = torch.get_rng_state(); cuda_rng = torch.cuda.get_rng_state()
    results = []
    config = FlowConfig(condition_dropout=0, self_condition_probability=1, time_mean=2, time_std=.1)
    try:
        for bucket, names in sorted(buckets.items()):
            # Fixed data-only choice; stress the strongest confidence downweighting.
            record = min((records[n] for n in names), key=lambda r: (float(r['residue_weights'].mean()), r['id']))
            batch = collate([record]); padding = bucket-len(record['sequence'])
            for k in ('z', 'ca', 'esm'):
                batch[k] = F.pad(batch[k], (0, 0, 0, padding))
            batch['mask'] = F.pad(batch['mask'], (0, padding))
            batch['residue_weights'] = F.pad(record['residue_weights'][None], (0, padding))
            batch = {k:v.cuda() if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
            control = dict(id=record['id'], bucket=bucket)
            for mode in ('fp32', 'fp16'):
                model.zero_grad(set_to_none=True)
                gen = torch.Generator(device='cuda').manual_seed(1729)
                with inference_precision(mode):
                    loss, _ = objective(model, decoder, batch, config, generator=gen)
                scale = 128 if mode == 'fp16' else 1
                (loss*scale).backward()
                grads = {n:p.grad.detach().div(scale) for n,p in model.named_parameters() if p.grad is not None}
                if not all(torch.isfinite(g).all() for g in grads.values()):
                    raise FloatingPointError('nonfinite confidence-weighted gradient')
                if mode == 'fp32':
                    reference = grads; control['fp32_loss'] = float(loss.detach())
                else:
                    if set(reference) != set(grads):
                        raise ValueError('mixed precision gradient coverage changed')
                    dot = sum((reference[n]*g).double().sum() for n,g in grads.items())
                    rr = sum(g.double().square().sum() for g in reference.values())
                    gg = sum(g.double().square().sum() for g in grads.values())
                    diff = sum((reference[n]-g).double().square().sum() for n,g in grads.items())
                    control.update(fp16_loss=float(loss.detach()), gradient_cosine=float(dot/(rr*gg).sqrt()), relative_l2=float((diff/rr).sqrt()))
            control['passed'] = (control['gradient_cosine'] >= .99 and control['relative_l2'] <= .1 and abs(control['fp16_loss']/control['fp32_loss']-1) <= .02)
            results.append(control)
            del reference, grads, loss, batch
            model.zero_grad(set_to_none=True); gc.collect(); torch.cuda.empty_cache()
        return results
    finally:
        model.zero_grad(set_to_none=True)
        torch.set_rng_state(rng); torch.cuda.set_rng_state(cuda_rng)
