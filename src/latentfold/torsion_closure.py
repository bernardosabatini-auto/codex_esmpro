"""One-start torsion closure, with fixed atoms and independently scored endpoints."""
import time
import numpy as np
import torch
from .internal_bridge import InternalBridge
from .local_closure import topology,distances


class TorsionClosure:
    def __init__(self,source,parent,start,motif_length,spec):
        self.source=torch.tensor(source,dtype=torch.float64)
        self.parent=torch.tensor(parent,dtype=torch.float64)
        if (self.source.shape!=self.parent.shape or not torch.isfinite(self.source).all()
                or not torch.isfinite(self.parent).all()):raise ValueError('Matching finite parent and fixed anchors required')
        self.spec=spec;width=spec['flank_width'];stop=start+motif_length
        self.models=(InternalBridge(self.parent,start-width,start),InternalBridge(self.parent,stop,stop+width))
        self.graph=topology(len(parent),start,motif_length,width)
        self.cutoffs=distances(self.parent.reshape(-1,3),self.graph['ca_pairs']).clamp_max(2.5)
        self.count=sum(m.n_torsions for m in self.models)

    def assemble(self,delta):
        if delta.shape!=(self.count,):raise ValueError('One offset per free phi/psi required')
        output=self.source;errors=[];offset=0
        for m in self.models:
            output,error=m.assemble(output,delta[offset:offset+m.n_torsions]);errors.append(error);offset+=m.n_torsions
        return output,torch.stack(errors)

    def loss(self,delta):
        output,error=self.assemble(delta);o=self.spec['objective']
        d=distances(output.reshape(-1,3),self.graph['ca_pairs'])
        parts=dict(endpoint=(error/o['endpoint_scale_angstrom']).square().mean(),
            clash=((self.cutoffs-d).clamp_min(0)/o['ca_clash_scale_angstrom']).square().mean(),
            displacement=o['torsion_displacement_weight']*delta.square().mean())
        total=sum(parts.values())
        if not torch.isfinite(total):raise FloatingPointError('Nonfinite torsion closure objective')
        return total,parts


def close_torsions(source,parent,start,motif_length,spec,*,deadline=None):
    tick=time.monotonic()
    if deadline is not None and tick>deadline:raise TimeoutError('Torsion closure CPU cap')
    source=np.asarray(source);parent=np.asarray(parent)
    s=spec['solver']
    if s['canonical_frame']!='parent_start_N_CA_C' or s['input_grid_angstrom']!=1e-6:
        raise ValueError('Unrecognized fixed numerical frame')
    origin=parent[start,1].astype(np.float64)
    x=parent[start,2].astype(np.float64)-origin;x/=np.linalg.norm(x)
    y=parent[start,0].astype(np.float64)-origin;y-=np.dot(x,y)*x;y/=np.linalg.norm(y)
    basis=np.stack((x,y,np.cross(x,y)),axis=1);grid=s['input_grid_angstrom']
    canonical_source=np.round(((source-origin)@basis)/grid)*grid
    canonical_parent=np.round(((parent-origin)@basis)/grid)*grid
    problem=TorsionClosure(canonical_source,canonical_parent,start,motif_length,spec)
    delta=torch.zeros(problem.count,dtype=torch.float64,requires_grad=True)
    before=float(problem.loss(delta)[0].detach());calls=0
    optimizer=torch.optim.LBFGS([delta],lr=s['lr'],max_iter=s['max_iter'],max_eval=s['max_eval'],
        history_size=s['history_size'],tolerance_grad=s['tolerance_grad'],tolerance_change=s['tolerance_change'],
        line_search_fn=s['line_search_fn'])
    def closure():
        nonlocal calls
        if deadline is not None and time.monotonic()>deadline:raise TimeoutError('Torsion closure CPU cap')
        optimizer.zero_grad(set_to_none=True);loss,_=problem.loss(delta);loss.backward();calls+=1;return loss
    # Numerical reconstruction may produce ~1e-24 loss for an exact parent.
    # Exact input equality permits a true no-op without a numerical optimizer.
    identical=np.array_equal(source,parent)
    if not identical:optimizer.step(closure)
    candidate,error=problem.assemble(delta);loss,parts=problem.loss(delta)
    result=source.copy();editable=problem.graph['residues']
    if not identical:result[editable]=candidate.detach().numpy()[editable]@basis.T+origin
    fixed=np.ones(len(source),dtype=bool);fixed[editable]=False
    if not np.array_equal(result[fixed],source[fixed]):raise ValueError('Torsion closure moved fixed atoms')
    return result,dict(seconds=time.monotonic()-tick,initial_loss=before,final_loss=float(loss.detach()),
        loss_terms={k:float(v.detach()) for k,v in parts.items()},torsion_offsets=delta.detach().tolist(),
        endpoint_rmsd_angstrom=error.detach().square().sum(-1).mean(-1).sqrt().tolist(),
        iterations=optimizer.state[delta].get('n_iter',0),closure_calls=calls,fixed_exact=True,exact_noop=identical)
