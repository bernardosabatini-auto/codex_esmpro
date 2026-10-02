"""Bijections of Gaussian/teacher draws strictly within one sequence condition."""
import numpy as np
import torch
from scipy.optimize import linear_sum_assignment


def couple_targets(noise,targets,mask,ids,*,group_size,arm):
    if arm not in ('independent','optimal') or type(group_size) is not int or group_size<2:raise ValueError('Unknown coupling recipe')
    if noise.shape!=targets.shape or noise.ndim!=3 or noise.shape[-1]!=8 or mask.shape!=noise.shape[:2] or mask.dtype!=torch.bool or len(ids)!=len(noise) or len(ids)%group_size:raise ValueError('Invalid coupling shapes')
    if targets.requires_grad or noise.requires_grad or targets.device!=noise.device or targets.dtype!=noise.dtype or not torch.isfinite(noise).all() or not torch.isfinite(targets).all():raise ValueError('Coupling requires fixed finite matched tensors')
    result=targets.clone();indices=[];costs=[]
    for start in range(0,len(ids),group_size):
        stop=start+group_size;m=mask[start]
        if len(set(ids[start:stop]))!=1 or not m.any() or not torch.equal(mask[start:stop],m[None].expand(group_size,-1)):raise ValueError('Coupling crossed sequence conditions')
        x=noise[start:stop,m].reshape(group_size,-1).double().cpu().numpy();z=targets[start:stop,m].reshape(group_size,-1).double().cpu().numpy()
        cost=(np.square(x).sum(1)[:,None]+np.square(z).sum(1)[None,:]-2*x@z.T)/x.shape[1]
        rows,cols=linear_sum_assignment(cost)
        if not np.array_equal(rows,np.arange(group_size)) or set(cols)!=set(range(group_size)):raise ValueError('Not a bijective assignment')
        before=float(np.diag(cost).mean());optimal=float(cost[rows,cols].mean())
        if optimal>before+1e-10:raise ValueError('Assignment increases transport cost')
        chosen=cols if arm=='optimal' else np.arange(group_size);result[start:stop]=targets[start:stop].index_select(0,torch.as_tensor(chosen,device=targets.device));indices.extend((chosen+start).tolist())
        costs.append(dict(independent=before,optimal=optimal,applied=optimal if arm=='optimal' else before))
    return result,dict(permutation=indices,costs=costs,groups=len(costs))
