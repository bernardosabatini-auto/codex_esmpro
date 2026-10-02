"""Fixed conditional latent-space refinement with conservative output acceptance."""
import numpy as np
import torch
from torch.nn import functional as F
from latentfold.backbone_repair import _angles, _volume
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.local_geometry import local_geometry_loss
from latentfold.metrics import ca_metrics


def accept(original, candidate, c):
    old, new = np.asarray(original, dtype=np.float64), np.asarray(candidate, dtype=np.float64)
    if old.shape != new.shape or old.ndim != 3 or old.shape[1:] != (4, 3) or not np.isfinite(new).all():
        return False, dict(invalid_candidate=True)
    motion = np.linalg.norm(new-old, axis=-1)
    before, after = backbone_geometry(old[None]), backbone_geometry(new[None])
    pair = lambda x: np.linalg.norm(x[:, :, None]-x[:, None, :], axis=-1)
    oldgap = np.linalg.norm(np.diff(old[:, 1], axis=0), axis=-1)
    newgap = np.linalg.norm(np.diff(new[:, 1], axis=0), axis=-1)
    peptide = np.linalg.norm(new[:-1, 2]-new[1:, 0], axis=-1)
    i, j = np.triu_indices(len(new), 3)
    clashes = np.linalg.norm(new[i, 1]-new[j, 1], axis=-1) < c['accept_clash']
    affected = np.unique(np.concatenate((i[clashes], j[clashes])))
    ov, nv = _volume(old[:, 1]), _volume(new[:, 1]); strong = np.abs(ov) > c['strong_volume_threshold']
    a, am, b, bm, w, wm = _angles(old); na, nam, nb, nbm, nw, nwm = _angles(new)
    angles = np.rad2deg(np.concatenate((np.abs(na-a)[am], np.abs(nb-b)[bm])))
    omega = np.rad2deg(np.abs(np.arctan2(np.sin(nw-w), np.cos(nw-w)))[wm])
    gates = dict(
        coarse_valid=bool(after['coarse_valid'][0]),
        bounded=motion.max() <= c['max_atom_motion'] and np.sqrt(np.mean(motion**2)) <= c['rms_atom_motion'],
        intraresidue_preserved=np.max(np.abs(pair(new)-pair(old))) <= c['max_intraresidue_distance_change'],
        defects_nonincreasing=all(after[k][0] <= before[k][0] for k in ('peptide_outlier_fraction','ca_clashing_residue_fraction','ca_gap_fraction')),
        buffered_valid=((peptide < c['accept_peptide'][0]) | (peptide > c['accept_peptide'][1])).mean() <= .05 and len(affected)/len(new) <= .01 and (newgap > c['accept_gap']).mean() <= .01,
        adjacent_preserved=np.all(np.abs(newgap-oldgap)[oldgap <= 4.5] <= c['max_adjacent_change']),
        handedness_preserved=np.all(ov[strong]*nv[strong] > 0),
        angles_preserved=np.all(nam[am]) and np.all(nbm[bm]) and np.all(nwm[wm]) and angles.max(initial=0) <= c['max_angle_change_degrees'] and omega.max(initial=0) <= c['max_omega_change_degrees'],
        contacts_preserved=ca_metrics(new[:, 1], old[:, 1])['ca_lddt'] >= c['minimum_ca_lddt_to_original'],
    )
    return all(gates.values()), dict(gates={k:bool(v) for k,v in gates.items()}, max_atom_motion=float(motion.max()), rms_atom_motion=float(np.sqrt(np.mean(motion**2))))


def repair(decoder, z, mask, noise, original, protocol):
    if backbone_geometry(original[None])['coarse_valid'][0]:
        return original.copy(), dict(status='unchanged_valid', steps=0)
    n = len(original); c = protocol['optimization']; start = z.detach().clone()
    variable = start.clone().requires_grad_(); optimizer = torch.optim.Adam([variable], lr=c['learning_rate'])
    reference = torch.as_tensor(original, device=z.device)[None]
    details = {}
    with torch.enable_grad():
        for step in range(1, c['steps']+1):
            _, bb = decoder(variable, mask, noise=noise, return_backbone=True)
            loss, _ = local_geometry_loss(bb, mask, c)
            loss = loss+c['latent_tether']*(variable[:,:n]-start[:,:n]).square().mean()+c['coordinate_tether']*(bb[:,:n]-reference).square().mean()
            optimizer.zero_grad(); loss.backward()
            if not torch.isfinite(loss) or not torch.isfinite(variable.grad).all():
                return original.copy(), dict(status='fallback_nonfinite', steps=step)
            optimizer.step()
            with torch.no_grad():
                projected = F.layer_norm(variable[:,:n], (8,))
                delta = projected-start[:,:n]
                delta *= torch.clamp(c['max_latent_rms']/delta.square().mean().sqrt().clamp_min(1e-12), max=1)
                variable[:,:n].copy_(start[:,:n]+delta); variable[:,n:].copy_(start[:,n:])
                _, candidate = decoder(variable, mask, noise=noise, return_backbone=True)
            candidate = candidate[0,:n].detach().cpu().numpy()
            accepted, details = accept(original, candidate, protocol['acceptance'])
            if accepted: return candidate, dict(status='repaired', steps=step, **details)
    return original.copy(), dict(status='fallback_constraints', steps=c['steps'], last_candidate=details)
