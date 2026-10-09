"""One prospective atom-repulsion addition; original closure implementation stays frozen."""
import time
import numpy as np
import torch
from .torsion_closure import TorsionClosure
from .local_closure import distances
from .backbone_sterics import nonbonded_pairs,steric_loss


class StericTorsionClosure(TorsionClosure):
    def __init__(self,source,parent,start,motif_length,spec,nonbonded):
        super().__init__(source,parent,start,motif_length,spec)
        if (nonbonded['exclude_covalent_distance_at_most']!=3 or nonbonded['cutoff_angstrom']!=2.5
                or nonbonded['scale_angstrom']!=.25 or nonbonded['coefficient']!=1):raise ValueError('Changed fixed atom-repulsion prescription')
        self.pairs=torch.tensor(nonbonded_pairs(len(parent),self.graph['residues']))
        x=self.parent.reshape(-1,3)
        self.atom_cutoffs=(x[self.pairs[:,0]]-x[self.pairs[:,1]]).norm(dim=-1).clamp_max(nonbonded['cutoff_angstrom'])
        self.nonbonded=nonbonded

    def loss(self,delta):
        output,error=self.assemble(delta);o=self.spec['objective']
        d=distances(output.reshape(-1,3),self.graph['ca_pairs'])
        parts=dict(endpoint=(error/o['endpoint_scale_angstrom']).square().mean(),
            clash=((self.cutoffs-d).clamp_min(0)/o['ca_clash_scale_angstrom']).square().mean(),
            displacement=o['torsion_displacement_weight']*delta.square().mean())
        original=sum(parts.values())
        atom=steric_loss(output,self.pairs,self.atom_cutoffs,scale=self.nonbonded['scale_angstrom'],
                        editable_atoms=4*len(self.graph['residues']))*self.nonbonded['coefficient']
        loss=original+atom
        if not torch.isfinite(loss):raise FloatingPointError('Nonfinite atom-repulsion closure')
        return loss,dict(parts,nonbonded=atom)


def close_steric_torsions(source,parent,start,motif_length,spec,nonbonded,*,deadline=None):
    tick=time.monotonic()
    if deadline is not None and tick>deadline:raise TimeoutError('Steric closure CPU cap')
    source=np.asarray(source);parent=np.asarray(parent);s=spec['solver']
    if s['canonical_frame']!='parent_start_N_CA_C' or s['input_grid_angstrom']!=1e-6:raise ValueError('Changed numerical frame')
    origin=parent[start,1].astype(np.float64)
    x=parent[start,2].astype(np.float64)-origin;x/=np.linalg.norm(x)
    y=parent[start,0].astype(np.float64)-origin;y-=np.dot(x,y)*x;y/=np.linalg.norm(y)
    basis=np.stack((x,y,np.cross(x,y)),axis=1);grid=s['input_grid_angstrom']
    cs=np.round(((source-origin)@basis)/grid)*grid;cp=np.round(((parent-origin)@basis)/grid)*grid
    problem=StericTorsionClosure(cs,cp,start,motif_length,spec,nonbonded)
    delta=torch.zeros(problem.count,dtype=torch.float64,requires_grad=True);before=float(problem.loss(delta)[0].detach());calls=0
    optimizer=torch.optim.LBFGS([delta],lr=s['lr'],max_iter=s['max_iter'],max_eval=s['max_eval'],
        history_size=s['history_size'],tolerance_grad=s['tolerance_grad'],tolerance_change=s['tolerance_change'],line_search_fn=s['line_search_fn'])
    def closure():
        nonlocal calls
        if deadline is not None and time.monotonic()>deadline:raise TimeoutError('Steric closure CPU cap')
        optimizer.zero_grad(set_to_none=True);loss,_=problem.loss(delta);loss.backward();calls+=1;return loss
    identical=np.array_equal(source,parent)
    if not identical:optimizer.step(closure)
    candidate,error=problem.assemble(delta);loss,parts=problem.loss(delta)
    result=source.copy();editable=problem.graph['residues']
    if not identical:result[editable]=candidate.detach().numpy()[editable]@basis.T+origin
    fixed=np.ones(len(source),dtype=bool);fixed[editable]=False
    if not np.array_equal(result[fixed],source[fixed]):raise ValueError('Fixed anchors moved')
    return result,dict(seconds=time.monotonic()-tick,initial_loss=before,final_loss=float(loss.detach()),
        loss_terms={k:float(v.detach()) for k,v in parts.items()},torsion_offsets=delta.detach().tolist(),
        endpoint_rmsd_angstrom=error.detach().square().sum(-1).mean(-1).sqrt().tolist(),
        iterations=optimizer.state[delta].get('n_iter',0),closure_calls=calls,fixed_exact=True,exact_noop=identical)
