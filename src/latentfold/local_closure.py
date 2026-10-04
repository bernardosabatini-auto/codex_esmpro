"""CPU-only local closure with exactly fixed motif and distant scaffold atoms.

Geometry targets come from the generated parent, not native scaffold coordinates.
Coordinates and displacements use Angstroms throughout.
"""
import itertools
import time
import numpy as np
import torch


def topology(length, start, motif_length, width):
    if not 0 <= start < start+motif_length <= length or motif_length < 1 or width < 1:
        raise ValueError('Contained motif and positive flank width required')
    residues=list(range(max(0,start-width),start))+list(range(start+motif_length,min(length,start+motif_length+width)))
    if not residues: raise ValueError('Editable scaffold required')
    atoms={4*r+a for r in residues for a in range(4)}
    bonds=[(4*r+a,4*r+b) for r in range(length) for a,b in ((0,1),(1,2),(2,3))]
    bonds += [(4*r+2,4*(r+1)) for r in range(length-1)]
    neighbors={i:[] for i in range(4*length)}
    for a,b in bonds:neighbors[a].append(b);neighbors[b].append(a)
    angles=[(a,c,b) for c,ns in neighbors.items() for a,b in itertools.combinations(sorted(ns),2)]
    torsions=[(4*r+a,4*r+2,4*(r+1),4*(r+1)+1) for r in range(length-1) for a in (1,3)]
    pairs=[(i,j) for i in range(length) for j in range(i+3,length) if i in residues or j in residues]
    def touched(rows):return torch.tensor([row for row in rows if atoms.intersection(row)],dtype=torch.long)
    return dict(residues=residues,editable=torch.tensor(sorted(atoms)),bonds=touched(bonds),angles=touched(angles),
                torsions=touched(torsions),ca_pairs=torch.tensor([(4*i+1,4*j+1) for i,j in pairs],dtype=torch.long).reshape(-1,2))


def distances(x, indices):
    return (x[indices[:,0]]-x[indices[:,1]]).norm(dim=-1)


def angle_cosines(x, indices):
    a=x[indices[:,0]]-x[indices[:,1]];b=x[indices[:,2]]-x[indices[:,1]]
    return (a*b).sum(-1)/(a.norm(dim=-1)*b.norm(dim=-1)).clamp_min(1e-12)


def torsion_vectors(x, indices):
    b0=x[indices[:,1]]-x[indices[:,0]];b1=x[indices[:,2]]-x[indices[:,1]];b2=x[indices[:,3]]-x[indices[:,2]]
    n1=torch.linalg.cross(b0,b1);n2=torch.linalg.cross(b1,b2)
    n1=n1/n1.norm(dim=-1,keepdim=True).clamp_min(1e-12)
    n2=n2/n2.norm(dim=-1,keepdim=True).clamp_min(1e-12)
    axis=b1/b1.norm(dim=-1,keepdim=True).clamp_min(1e-12)
    return torch.stack(((n1*n2).sum(-1),(torch.linalg.cross(n1,n2)*axis).sum(-1)),dim=-1)


class ClosureProblem:
    def __init__(self, source, parent, start, motif_length, spec):
        source=np.asarray(source);parent=np.asarray(parent)
        if (source.ndim!=3 or source.shape[1:]!=(4,3) or parent.shape!=source.shape
                or not np.isfinite(source).all() or not np.isfinite(parent).all()):
            raise ValueError('Finite matching N/CA/C/O backbones required')
        self.spec=spec;self.graph=topology(len(source),start,motif_length,spec['solver']['width'])
        self.source=torch.tensor(source.reshape(-1,3),dtype=torch.float64)
        self.parent=torch.tensor(parent.reshape(-1,3),dtype=torch.float64)
        g=self.graph;x=self.parent
        self.target_bonds=distances(x,g['bonds']);self.target_angles=angle_cosines(x,g['angles'])
        self.target_torsions=torsion_vectors(x,g['torsions'])
        if ((self.target_bonds<1e-6).any() or (self.target_angles.abs()>1-1e-8).any()
                or (self.target_torsions.norm(dim=-1)<.999999).any()):
            raise ValueError('Degenerate generated-parent geometry')
        self.clash_cutoffs=distances(x,g['ca_pairs']).clamp_max(2.5)

    def assemble(self, editable):
        return self.source.index_copy(0,self.graph['editable'],editable)

    def loss(self, editable):
        x=self.assemble(editable);g=self.graph;o=self.spec['objective']
        terms=dict(bond=((distances(x,g['bonds'])-self.target_bonds)/o['bond_scale_angstrom']).square().mean(),
            angle=((angle_cosines(x,g['angles'])-self.target_angles)/o['angle_cosine_scale']).square().mean(),
            peptide=((torsion_vectors(x,g['torsions'])-self.target_torsions)/o['peptide_torsion_sincos_scale']).square().mean(),
            clash=((self.clash_cutoffs-distances(x,g['ca_pairs'])).clamp_min(0)/o['ca_clash_scale_angstrom']).square().mean() if len(g['ca_pairs']) else x.sum()*0,
            displacement=o['displacement_weight']*(editable-self.source[g['editable']]).square().mean())
        total=sum(terms.values())
        if not torch.isfinite(total):raise FloatingPointError('Nonfinite closure objective')
        return total,terms


def geometry_audit(backbone,parent,start,motif_length,width=4):
    """Independent NumPy evaluation of all touched bonds, angles and torsions."""
    bb=np.asarray(backbone,dtype=np.float64).reshape(-1,3);ref=np.asarray(parent,dtype=np.float64).reshape(-1,3)
    if not np.isfinite(bb).all() or bb.shape!=ref.shape:raise ValueError('Invalid closure output')
    graph=topology(len(bb)//4,start,motif_length,width)
    edges=graph['bonds'].numpy();angles=graph['angles'].numpy();torsions=graph['torsions'].numpy()
    def lengths(x):return np.linalg.norm(x[edges[:,0]]-x[edges[:,1]],axis=-1)
    def degrees(x):
        a=x[angles[:,0]]-x[angles[:,1]];b=x[angles[:,2]]-x[angles[:,1]]
        return np.degrees(np.arctan2(np.linalg.norm(np.cross(a,b),axis=-1),(a*b).sum(-1)))
    def dihedral(x):
        b0=x[torsions[:,1]]-x[torsions[:,0]];b1=x[torsions[:,2]]-x[torsions[:,1]];b2=x[torsions[:,3]]-x[torsions[:,2]]
        n1=np.cross(b0,b1);n2=np.cross(b1,b2)
        norms=np.linalg.norm(n1,axis=-1)*np.linalg.norm(n2,axis=-1)
        if np.any(norms<1e-12):raise ValueError('Degenerate output torsion')
        return np.degrees(np.arctan2((np.cross(n1,n2)*b1).sum(-1)/np.linalg.norm(b1,axis=-1),(n1*n2).sum(-1)))
    bond_delta=np.abs(lengths(bb)-lengths(ref));angle_delta=np.abs(degrees(bb)-degrees(ref))
    torsion_delta=np.abs((dihedral(bb)-dihedral(ref)+180)%360-180)
    return dict(bonds=edges.tolist(),bond_lengths=lengths(bb).tolist(),parent_bond_lengths=lengths(ref).tolist(),
        angles=angles.tolist(),angle_degrees=degrees(bb).tolist(),parent_angle_degrees=degrees(ref).tolist(),
        torsions=torsions.tolist(),torsion_degrees=dihedral(bb).tolist(),parent_torsion_degrees=dihedral(ref).tolist(),
        max_bond_delta=float(bond_delta.max()),max_angle_delta=float(angle_delta.max()),max_torsion_delta=float(torsion_delta.max()),
        valid=bool((bond_delta<=.05).all() and (angle_delta<=10).all() and (torsion_delta<=10).all()))


def close_backbone(source,parent,start,motif_length,spec,*,deadline=None):
    tick=time.monotonic()
    if deadline is not None and tick>deadline:raise TimeoutError('CPU closure work cap')
    origin,basis=None,None
    if spec['solver'].get('canonical_frame'):
        if spec['solver']['canonical_frame']!='parent_start_N_CA_C':raise ValueError('Unknown closure frame')
        reference=np.asarray(parent,dtype=np.float64);original=np.asarray(source,dtype=np.float64)
        origin=reference[start,1];x_axis=reference[start,2]-origin;x_axis=x_axis/np.linalg.norm(x_axis)
        y_axis=reference[start,0]-origin;y_axis=y_axis-np.dot(y_axis,x_axis)*x_axis
        if np.linalg.norm(y_axis)<1e-6:raise ValueError('Degenerate parent frame')
        y_axis=y_axis/np.linalg.norm(y_axis);basis=np.stack([x_axis,y_axis,np.cross(x_axis,y_axis)],axis=1)
        grid=spec['solver']['input_grid_angstrom']
        if grid!=1e-6:raise ValueError('Changed numerical input grid')
        canonical_source=np.round(((original-origin)@basis)/grid)*grid
        canonical_parent=np.round(((reference-origin)@basis)/grid)*grid
        problem=ClosureProblem(canonical_source,canonical_parent,start,motif_length,spec)
    else:
        problem=ClosureProblem(source,parent,start,motif_length,spec)
    x=problem.source[problem.graph['editable']].clone().requires_grad_();s=spec['solver']
    before=float(problem.loss(x)[0].detach());calls=0
    optimizer=torch.optim.LBFGS([x],lr=s['lr'],max_iter=s['max_iter'],max_eval=s['max_eval'],
        tolerance_grad=s['tolerance_grad'],tolerance_change=s['tolerance_change'],history_size=s['history_size'],line_search_fn='strong_wolfe')
    def closure():
        nonlocal calls
        if deadline is not None and time.monotonic()>deadline:raise TimeoutError('CPU closure work cap')
        optimizer.zero_grad(set_to_none=True);loss,_=problem.loss(x);loss.backward();calls+=1;return loss
    if before!=0:optimizer.step(closure)
    loss,parts=problem.loss(x)
    result=np.asarray(source).copy().reshape(-1,3)
    if before!=0:
        moving=x.detach().numpy()
        if basis is not None:moving=moving@basis.T+origin
        result[problem.graph['editable'].numpy()]=moving
    result=result.reshape(np.asarray(source).shape)
    fixed=np.ones(len(result)*4,dtype=bool);fixed[problem.graph['editable'].numpy()]=False
    if not np.array_equal(result.reshape(-1,3)[fixed],np.asarray(source).reshape(-1,3)[fixed]):
        raise ValueError('Closure moved fixed atoms')
    return result,dict(seconds=time.monotonic()-tick,initial_loss=before,final_loss=float(loss.detach()),
        terms={k:float(v.detach()) for k,v in parts.items()},closure_calls=calls,iterations=optimizer.state[x].get('n_iter',0),
        max_editable_displacement=float(np.linalg.norm(result-np.asarray(source),axis=-1).max()))
