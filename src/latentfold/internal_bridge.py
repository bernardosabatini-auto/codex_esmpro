"""Differentiable local backbone kinematics; endpoint closure is NOT imposed.

Lengths, angles and peptide omega come from the supplied generated parent.
Only phi/psi vary. Oxygen follows its peptide plane, not a fixed global offset.
The reconstructed right endpoint is returned as a ghost: callers must measure
its residual against the fixed endpoint before claiming a connected backbone.
Units are Angstrom and radians. This implementation handles interior bridges.
"""
import torch


def _unit(x):
    norm=x.norm(dim=-1,keepdim=True)
    if (norm<1e-10).any():raise ValueError('Degenerate kinematic frame')
    return x/norm


def internal(a,b,c,d):
    """Bond length C-D, angle B-C-D, signed dihedral A-B-C-D."""
    u=_unit(c-b);n=_unit(torch.linalg.cross(b-a,u));v=torch.linalg.cross(n,u)
    displacement=d-c;length=displacement.norm(dim=-1)
    if (length<1e-10).any():raise ValueError('Degenerate bond')
    axial=(displacement*u).sum(-1)
    planar=(displacement*v).sum(-1);normal=(displacement*n).sum(-1)
    radius=torch.sqrt(planar.square()+normal.square())
    if (radius<1e-10).any():raise ValueError('Degenerate bond angle')
    return length,torch.atan2(radius,-axial),torch.atan2(normal,planar)


def place(a,b,c,length,angle,torsion):
    u=_unit(c-b);n=_unit(torch.linalg.cross(b-a,u));v=torch.linalg.cross(n,u)
    direction=(-torch.cos(angle)[...,None]*u+torch.sin(angle)[...,None]*(
        torch.cos(torsion)[...,None]*v+torch.sin(torsion)[...,None]*n))
    return c+length[...,None]*direction


class InternalBridge:
    def __init__(self,reference,lo,hi):
        """Rebuild residues [lo,hi), between two fixed complete residues."""
        if (reference.ndim!=3 or reference.shape[1:]!=(4,3) or not reference.is_floating_point()
                or not torch.isfinite(reference).all() or reference.requires_grad
                or not 0<lo<hi<len(reference)):
            raise ValueError('Finite detached backbone and interior nonempty bridge required')
        self.lo,self.hi,self.shape=lo,hi,reference.shape
        spine=reference[lo-1:hi+1,:3].reshape(-1,3)
        a,b,c,d=spine[:-3],spine[1:-2],spine[2:-1],spine[3:]
        length,angle,torsion=internal(a,b,c,d)
        # Use the fixed left carbonyl O to hold the first peptide plane.
        first=internal(reference[lo-1,3],reference[lo-1,1],reference[lo-1,2],reference[lo,0])
        self.length=torch.cat((first[0][None],length[1:]))
        self.angle=torch.cat((first[1][None],angle[1:]))
        self.torsion=torch.cat((first[2][None],torsion[1:]))
        # N placement is psi, CA placement is omega, C placement is phi.
        self.free=[i for i in range(len(length)) if i>0 and i%3!=1]
        self.oxygen=internal(reference[lo+1:hi+1,0],reference[lo:hi,1],
                             reference[lo:hi,2],reference[lo:hi,3])

    @property
    def n_torsions(self):return len(self.free)

    def reconstruct(self,source,delta):
        if (source.shape!=self.shape or source.dtype!=self.length.dtype or source.device!=self.length.device
                or delta.shape!=(self.n_torsions,) or delta.dtype!=source.dtype or delta.device!=source.device
                or not torch.isfinite(source).all() or not torch.isfinite(delta).all()):
            raise ValueError('Matching finite source and torsion offsets required')
        index=torch.tensor(self.free,device=delta.device)
        torsion=self.torsion.index_add(0,index,delta)
        chain=list(source[self.lo-1,:3].unbind())
        for j in range(len(torsion)):
            a,b,c=chain[-3:]
            if j==0:a=source[self.lo-1,3]
            chain.append(place(a,b,c,self.length[j],self.angle[j],torsion[j]))
        spine=torch.stack(chain[3:]).reshape(self.hi-self.lo+1,3,3)
        oxygen=place(spine[1:,0],spine[:-1,1],spine[:-1,2],*self.oxygen)
        editable=torch.cat((spine[:-1],oxygen[:,None]),dim=1)
        return editable,spine[-1]

    def assemble(self,source,delta):
        editable,endpoint=self.reconstruct(source,delta)
        # Fixed coordinates are copied exactly. Endpoint mismatch stays visible.
        output=torch.cat((source[:self.lo],editable,source[self.hi:]),dim=0)
        return output,endpoint-source[self.hi,:3]
