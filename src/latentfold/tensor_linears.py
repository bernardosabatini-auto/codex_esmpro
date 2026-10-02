"""Experimental inference-only TF32x3 linears; float32 storage is unchanged.

This arithmetic is separately qualified, not labeled IEEE FP32 or enabled by
default. Pair/attention products, normalization, modulation and decoder stay
on their original paths. Import does not initialize CUDA or compile kernels.
"""
from contextlib import contextmanager
import torch
import triton
import triton.language as tl


@triton.jit
def _linear(X,W,B,Y,M,N:tl.constexpr,K:tl.constexpr,HAS_BIAS:tl.constexpr,
            PRECISION:tl.constexpr,BM:tl.constexpr=64,BN:tl.constexpr=64,BK:tl.constexpr=32):
    rows=tl.program_id(0)*BM+tl.arange(0,BM)
    cols=tl.program_id(1)*BN+tl.arange(0,BN)
    kk=tl.arange(0,BK)
    acc=tl.full((BM,BN),0,tl.float32)
    for offset in range(tl.cdiv(K,BK)):
        k=offset*BK+kk
        a=tl.load(X+rows[:,None]*K+k[None,:],(rows[:,None]<M)&(k[None,:]<K),0)
        b=tl.load(W+cols[None,:]*K+k[:,None],(cols[None,:]<N)&(k[:,None]<K),0)
        acc=tl.dot(a,b,acc,input_precision=PRECISION)
    if HAS_BIAS:acc+=tl.load(B+cols,cols<N,0)[None,:]
    tl.store(Y+rows[:,None]*N+cols[None,:],acc,(rows[:,None]<M)&(cols[None,:]<N))


def tensor_linear(x,weight,bias=None,*,precision='tf32x3'):
    if precision not in ('tf32x3','tf32','ieee'):raise ValueError('unknown dot precision')
    if x.ndim<2 or weight.ndim!=2 or x.shape[-1]!=weight.shape[1] or x.numel()==0:raise ValueError('invalid linear shapes')
    tensors=[x,weight]+([bias] if bias is not None else [])
    if any(v.dtype!=torch.float32 or not v.is_cuda or v.device!=x.device for v in tensors):raise ValueError('same-device CUDA float32 inputs required')
    if bias is not None and bias.shape!=(weight.shape[0],):raise ValueError('invalid bias shape')
    if torch.is_grad_enabled() and any(v.requires_grad for v in tensors):raise ValueError('experimental linear has no backward implementation')
    a=x.reshape(-1,x.shape[-1]).contiguous();w=weight.contiguous();b=bias.contiguous() if bias is not None else None
    m,k=a.shape;n=w.shape[0];y=torch.empty((m,n),device=x.device,dtype=torch.float32)
    _linear[(triton.cdiv(m,64),triton.cdiv(n,64))](a,w,b if b is not None else y,y,m,n,k,b is not None,precision,num_warps=4,num_stages=2)
    return y.reshape(*x.shape[:-1],n)


class _TensorLinear(torch.nn.Module):
    def __init__(self,inner):
        super().__init__();self.inner=inner;self.train(inner.training)
    def forward(self,x):
        if self.training:raise ValueError('experimental linear is inference-only')
        return tensor_linear(x,self.inner.weight,self.inner.bias)


@contextmanager
def tensor_core_linears(model):
    if model.training:raise ValueError('experimental linears are inference-only')
    originals=[]
    try:
        for block in model.blocks:
            for parent,name in ((block.mlp,'0'),(block.mlp,'3'),(block.attn,'qkv'),(block.attn,'out')):
                original=getattr(parent,name)
                if not isinstance(original,torch.nn.Linear):raise ValueError('unsupported or already wrapped linear')
                originals.append((parent,name,original));setattr(parent,name,_TensorLinear(original))
        yield
    finally:
        for parent,name,original in reversed(originals):setattr(parent,name,original)
