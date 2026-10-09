"""Whole-chain internal coordinates with an exact, isolated four-atom motif.

Parallel prefix products build each chain half in logarithmic sequential depth.
No distant coordinates are fixed, and no latent channels are rotated.
"""
import torch


def unit(x):
    length=torch.linalg.vector_norm(x,dim=-1,keepdim=True)
    if (length<=1e-8).any() or not torch.isfinite(length).all():raise ValueError('Degenerate backbone frame')
    return x/length


def frames(points):
    # points ends with three ordered atoms, followed by xyz.
    e1=unit(points[...,2,:]-points[...,1,:])
    e3=unit(torch.cross(points[...,1,:]-points[...,0,:],e1,dim=-1))
    e2=torch.cross(e3,e1,dim=-1)
    return torch.stack((e1,e2,e3),dim=-1)


def encode(backbone):
    if backbone.ndim!=4 or backbone.shape[2:]!=(4,3) or backbone.shape[1]<3 or not torch.isfinite(backbone).all():
        raise ValueError('Finite B,L,4,3 backbones required')
    chain=backbone[:,:,:3].flatten(1,2);bonds=chain[:,1:]-chain[:,:-1];directions=unit(bonds)
    lengths=torch.linalg.vector_norm(bonds,dim=-1)
    cosine=-(directions[:,:-1]*directions[:,1:]).sum(-1)
    sine=torch.linalg.vector_norm(torch.cross(directions[:,:-1],directions[:,1:],dim=-1),dim=-1)
    if (sine<=1e-8).any():raise ValueError('Collinear backbone atoms')
    angles=torch.atan2(sine,cosine)
    n0=unit(torch.cross(bonds[:,:-2],bonds[:,1:-1],dim=-1));n1=unit(torch.cross(bonds[:,1:-1],bonds[:,2:],dim=-1))
    torsions=torch.atan2((torch.cross(n0,n1,dim=-1)*directions[:,1:-1]).sum(-1),(n0*n1).sum(-1))
    # Oxygen is represented in the corresponding N-CA-C local frame at C.
    local=(frames(backbone[:,:,:3]).transpose(-1,-2)@(backbone[:,:,3]-backbone[:,:,2])[...,None]).squeeze(-1)
    return dict(lengths=lengths,angles=angles,torsions=torsions,oxygen=local)


def prefix_products(transforms):
    if transforms.ndim!=4 or transforms.shape[-2:]!=(4,4):raise ValueError('B,N,4,4 transforms required')
    result=transforms;offset=1
    while offset<transforms.shape[1]:
        result=torch.cat((result[:,:offset],result[:,:-offset]@result[:,offset:]),dim=1);offset*=2
    return result


def extend(seed,lengths,angles,torsions):
    if lengths.shape!=angles.shape or lengths.shape!=torsions.shape:raise ValueError('Unequal internal coordinate lengths')
    b,n=lengths.shape
    if n==0:return seed.new_empty((b,0,3))
    ct,st=torch.cos(angles),torch.sin(angles);cp,sp=torch.cos(torsions),torch.sin(torsions)
    v=torch.stack((-ct,st*cp,st*sp),-1)
    w=torch.stack((-st,-ct*cp,-ct*sp),-1)
    normal=torch.stack((torch.zeros_like(cp),-sp,cp),-1)
    rotation=torch.stack((v,w,normal),-1)
    top=torch.cat((rotation,(lengths[...,None]*v)[...,None]),-1)
    bottom=torch.zeros_like(top[:,:,:1]);bottom[:,:,:,3]=1
    transforms=prefix_products(torch.cat((top,bottom),-2))
    return seed[:,-1,None]+(frames(seed)[:,None]@transforms[:,:,:3,3,None]).squeeze(-1)


def decode(parameters,fragment,start):
    lengths,angles,torsions=(parameters[k] for k in ('lengths','angles','torsions'))
    oxygen=parameters['oxygen'];b,n=oxygen.shape[:2]
    if (fragment.ndim!=4 or fragment.shape[0]!=b or fragment.shape[2:]!=(4,3)
            or not 0<=start<=n-fragment.shape[1] or lengths.shape!=(b,3*n-1)
            or angles.shape!=(b,3*n-2) or torsions.shape!=(b,3*n-3)
            or not all(torch.isfinite(x).all() for x in (*parameters.values(),fragment))):
        raise ValueError('Finite compatible parameters and contained motif required')
    size=fragment.shape[1];end=3*(start+size);anchor=fragment[:,:,:3].flatten(1,2)
    if anchor.shape[1]<3:raise ValueError('At least one complete anchored residue required')
    right=extend(anchor[:,-3:],lengths[:,end-1:],angles[:,end-2:],torsions[:,end-3:])
    reverse_end=3*(n-start)
    left=extend(anchor.flip(1)[:,-3:],lengths.flip(1)[:,reverse_end-1:],angles.flip(1)[:,reverse_end-2:],torsions.flip(1)[:,reverse_end-3:]).flip(1)
    chain=torch.cat((left,anchor,right),1).reshape(b,n,3,3)
    o=chain[:,:,2]+(frames(chain)@oxygen[...,None]).squeeze(-1)
    o=torch.cat((o[:,:start],fragment[:,:,3],o[:,start+size:]),1)
    return torch.cat((chain,o[:,:,None]),2)
