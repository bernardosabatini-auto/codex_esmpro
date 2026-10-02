"""Decoded motif-shape supervision using only the supplied fragment atoms."""
import torch
from torch.nn import functional as F
from .flow import target_noise


def proper_motif_mse(predicted_ca, supplied_ca, keep):
    """Protein-mean squared RMSD after proper rotation, in Angstrom squared.

    Solve the alignment without differentiating through the SVD. At the optimum,
    the envelope derivative is the derivative of the residual with rotation fixed;
    this also avoids unstable SVD gradients for nearly planar fragments.
    """
    if predicted_ca.shape!=supplied_ca.shape or predicted_ca.shape!=(*keep.shape,3) or keep.dtype!=torch.bool or not (keep.sum(1)>=3).all():raise ValueError('Matching CA arrays and at least3supplied residues required')
    if not torch.isfinite(predicted_ca).all() or not torch.isfinite(supplied_ca).all() or supplied_ca.requires_grad:raise ValueError('Finite predictions and fixed fragment targets required')
    losses=[]
    for pred,ref,mask in zip(predicted_ca,supplied_ca,keep):
        x,y=pred[mask],ref[mask];x=x-x.mean(0);y=y-y.mean(0)
        with torch.no_grad():
            u,_,vh=torch.linalg.svd(x.detach().double().T@y.double());sign=torch.linalg.det(u@vh);diagonal=torch.eye(3,dtype=torch.float64,device=x.device);diagonal[-1,-1]=sign;rotation=(u@diagonal@vh).to(x)
        losses.append(((x@rotation-y).square().sum(-1)).mean())
    result=torch.stack(losses).mean()
    if not torch.isfinite(result):raise FloatingPointError('Nonfinite decoded motif objective')
    return result


def endpoint_fragment_objective(decoder,state,ids,lengths,coordinates,keep,*,step,seed=2026100235,maximum_examples=2,minimum_time=.25,maximum_time=.75):
    """Independent decoder-noise/subset streams leave flow draws unchanged."""
    eligible=torch.where((state['t']>=minimum_time)&(state['t']<=maximum_time)&~state['dropped'])[0];generator=torch.Generator().manual_seed(seed+step);chosen=eligible[torch.randperm(len(eligible),generator=generator)[:maximum_examples].to(eligible.device)];stats=dict(motif_examples=len(chosen),motif_mse=0.,chosen_slots=chosen.tolist())
    if not len(chosen):return None,stats
    t=state['t'][chosen,None,None];z=F.layer_norm(state['x'][chosen]+(1-t)*state['velocity'][chosen],(8,)).float();slots=chosen.tolist();mask=state['mask'][chosen]
    noise=target_noise([f'{ids[i]}:slot{i}' for i in slots],[4*lengths[i] for i in slots],3,seed=seed,sample_index=step,stream='fragment_objective_decoder',device=z.device);noise=F.pad(noise,(0,0,0,4*z.shape[1]-noise.shape[1]))*decoder.fm.scale_ref
    ca=decoder(z,mask,noise=noise);loss=proper_motif_mse(ca,coordinates[chosen],keep[chosen]);stats['motif_mse']=float(loss.detach());return loss,stats
