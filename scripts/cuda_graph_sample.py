"""Experimental static-shape CFG1/Euler25 sampler; default inference is unchanged."""
import torch
from torch.nn import functional as F
from latentfold.flow import validate_batch


def flow_body(net, esm, mask, noise):
    """Exact compact single-sequence arithmetic, with validation outside capture."""
    pair = net.compute_pair(esm, mask)
    prepared = net.prepare_condition(esm, mask, pair=pair)
    del pair
    x, sc = noise.clone(), None
    ts = torch.linspace(0, 1, 26, device=esm.device)
    for i in range(25):
        v = net(x, ts[i].expand(len(noise)), esm, mask, None, sc, prepared=prepared)
        if net.self_cond: sc = x+(1-ts[i])*v
        x = x+v*(ts[i+1]-ts[i])
    return F.layer_norm(x, (8,))*mask.unsqueeze(-1)


def validate(esm, mask, noise):
    validate_batch(esm, mask)
    if len(esm) != 1 or noise.ndim != 3 or noise.shape[1:] != (esm.shape[1],8) or len(noise)<1:
        raise ValueError('one sequence and complete fixed-shape ensemble required')
    if esm.dtype != torch.float32 or noise.dtype != torch.float32 or not torch.isfinite(noise).all():
        raise ValueError('finite FP32 inputs required')


class CapturedFlow:
    def __init__(self, net, esm, mask, noise):
        validate(esm,mask,noise)
        if net.training or torch.is_grad_enabled() or not esm.is_cuda or torch.is_autocast_enabled('cuda'):
            raise ValueError('capture requires CUDA eval, no_grad and strict FP32')
        if any(p.requires_grad or p.dtype!=torch.float32 for p in net.parameters()):
            raise ValueError('frozen FP32 model required')
        self.net=net;self.esm=esm.clone();self.mask=mask.clone();self.noise=noise.clone()
        side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):
            for _ in range(2):warm=flow_body(net,self.esm,self.mask,self.noise)
        torch.cuda.current_stream().wait_stream(side);del warm;torch.cuda.synchronize()
        self.graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph,stream=side):self.output=flow_body(net,self.esm,self.mask,self.noise)
        torch.cuda.synchronize()

    def __call__(self, esm, mask, noise):
        validate(esm,mask,noise)
        if self.net.training or torch.is_grad_enabled() or torch.is_autocast_enabled('cuda'):
            raise ValueError('captured inference mode changed')
        if esm.shape!=self.esm.shape or mask.shape!=self.mask.shape or noise.shape!=self.noise.shape:
            raise ValueError('captured shapes changed')
        if any(t.device!=self.esm.device for t in (esm,mask,noise)):
            raise ValueError('captured device changed')
        self.esm.copy_(esm);self.mask.copy_(mask);self.noise.copy_(noise);self.graph.replay()
        if not torch.isfinite(self.output).all():raise FloatingPointError('nonfinite captured output')
        return self.output.clone()
