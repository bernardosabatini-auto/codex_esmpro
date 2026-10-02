"""Bounded reference-free residue translations; retain original on any failed gate."""
import numpy as np
import torch
from .ensemble_metrics import backbone_geometry


def _angles(bb):
    def angle(a, b, c):
        u, v = a-b, c-b
        norm = np.linalg.norm(u, axis=-1)*np.linalg.norm(v, axis=-1)
        return np.arccos(np.clip((u*v).sum(-1)/np.maximum(norm, 1e-12), -1, 1)), norm > 1e-6
    ca, c, n, next_ca = bb[:-1, 1], bb[:-1, 2], bb[1:, 0], bb[1:, 1]
    a, am = angle(ca, c, n)
    b, bm = angle(c, n, next_ca)
    axis = n-c
    length = np.linalg.norm(axis, axis=-1)
    axis = axis/np.maximum(length[:, None], 1e-12)
    v, w = ca-c, next_ca-n
    v = v-(v*axis).sum(-1, keepdims=True)*axis
    w = w-(w*axis).sum(-1, keepdims=True)*axis
    omega = np.arctan2((np.cross(axis, v)*w).sum(-1), (v*w).sum(-1))
    mask = (length > 1e-6) & (np.linalg.norm(v, axis=-1) > 1e-6) & (np.linalg.norm(w, axis=-1) > 1e-6)
    return a, am, b, bm, omega, mask


def _volume(ca):
    d = np.diff(ca, axis=0)
    return (np.cross(d[:-2], d[1:-1])*d[2:]).sum(-1)/(3.8**3)


def acceptance(original, candidate, config):
    """All gates operate on the returned dtype, never higher-precision surrogates."""
    c = config
    old, new = np.asarray(original), np.asarray(candidate)
    if old.shape != new.shape or not np.isfinite(new).all():
        return False, {"reason": "invalid_candidate"}
    old, new = old.astype(np.float64), new.astype(np.float64)
    delta = new-old
    moves = np.linalg.norm(delta[:, 1], axis=-1)
    details = dict(max_translation=float(moves.max()), rms_translation=float(np.sqrt(np.mean(moves**2))))
    # Casting to float32 can introduce tiny per-atom differences.
    translation_only = float(np.max(np.abs(delta-delta[:, 1:2]))) <= 2e-5
    bounded = details['max_translation'] <= c['max_translation']+2e-5 and details['rms_translation'] <= c['max_rms_translation']
    before, after = backbone_geometry(old[None]), backbone_geometry(new[None])
    fractions = ('peptide_outlier_fraction', 'ca_clashing_residue_fraction', 'ca_gap_fraction')
    monotone = all(after[k][0] <= before[k][0] for k in fractions)
    peptide = np.linalg.norm(new[:-1, 2]-new[1:, 0], axis=-1)
    ca = new[:, 1]
    i, j = np.triu_indices(len(ca), 3)
    contact = np.linalg.norm(ca[i]-ca[j], axis=-1) < c['accept_clash']
    clash_residues = np.unique(np.concatenate((i[contact], j[contact])))
    buffered = ((peptide < c['accept_peptide'][0]) | (peptide > c['accept_peptide'][1])).mean() <= .05 and len(clash_residues)/len(ca) <= .01 and (np.linalg.norm(np.diff(ca, axis=0), axis=-1) > c['accept_gap']).mean() <= .01
    old_gap = np.linalg.norm(np.diff(old[:, 1], axis=0), axis=-1)
    new_gap = np.linalg.norm(np.diff(ca, axis=0), axis=-1)
    adjacent = np.all(np.abs(new_gap-old_gap)[old_gap <= 4.5] <= c['max_adjacent_change'])
    old_v, new_v = _volume(old[:, 1]), _volume(ca)
    strong = np.abs(old_v) > c['strong_volume_threshold']
    handed = np.all(old_v[strong]*new_v[strong] > 0)
    a, am, b, bm, w, wm = _angles(old)
    na, nam, nb, nbm, nw, nwm = _angles(new)
    angle_changes = np.concatenate((np.abs(na-a)[am], np.abs(nb-b)[bm]))
    omega_changes = np.abs(np.arctan2(np.sin(nw-w), np.cos(nw-w)))[wm]
    details['max_angle_change_degrees'] = float(np.rad2deg(angle_changes).max(initial=0))
    details['max_omega_change_degrees'] = float(np.rad2deg(omega_changes).max(initial=0))
    angles = np.all(nam[am]) and np.all(nbm[bm]) and np.all(nwm[wm]) and details['max_angle_change_degrees'] <= c['max_angle_change_degrees'] and details['max_omega_change_degrees'] <= c['max_omega_change_degrees']
    gates = dict(translation_only=translation_only, bounded=bounded, coarse_valid=bool(after['coarse_valid'][0]), defects_nonincreasing=monotone, buffered_valid=buffered, adjacent_preserved=adjacent, handedness_preserved=handed, angles_preserved=angles)
    details['gates'] = {k: bool(v) for k, v in gates.items()}
    return all(gates.values()), details


def repair_backbone(backbone, config):
    """CPU float64 optimization; output retains input dtype and sample identity."""
    bb = np.asarray(backbone)
    if bb.ndim != 3 or bb.shape[1:] != (4, 3) or len(bb) < 4 or bb.dtype not in (np.float32, np.float64) or not np.isfinite(bb).all():
        raise ValueError('expected finite floating [residues>=4,4,3] backbone')
    c = config
    if c['neighbor_radius'] < c['clash_target']+2*c['max_translation']:
        raise ValueError('neighbor list cannot cover bounded motion')
    if backbone_geometry(bb[None])['coarse_valid'][0]:
        return bb.copy(), dict(status='unchanged_valid', steps=0)
    x = torch.as_tensor(bb.astype(np.float64))
    i, j = np.triu_indices(len(bb), 3)
    near = np.linalg.norm(bb[i, 1].astype(np.float64)-bb[j, 1], axis=-1) < c['neighbor_radius']
    i, j = torch.as_tensor(i[near]), torch.as_tensor(j[near])
    shift = torch.zeros((len(bb), 3), dtype=x.dtype, requires_grad=True)
    optimizer = torch.optim.Adam([shift], lr=c['learning_rate'])
    norm = lambda t: torch.linalg.vector_norm(t, dim=-1)
    adjacent = norm(x[1:, 1]-x[:-1, 1])
    cross_a = norm(x[:-1, 1]-x[1:, 0])
    cross_b = norm(x[:-1, 2]-x[1:, 1])
    details = {}
    for step in range(1, c['steps']+1):
        y = x+shift[:, None]
        peptide = norm(y[:-1, 2]-y[1:, 0])
        gap = norm(y[1:, 1]-y[:-1, 1])
        loss = (torch.relu(c['peptide_target'][0]-peptide).square().sum()+torch.relu(peptide-c['peptide_target'][1]).square().sum()+torch.relu(c['clash_target']-norm(y[i, 1]-y[j, 1])).square().sum()+torch.relu(gap-c['gap_target']).square().sum())/len(bb)
        preserve = (gap-adjacent).square()[adjacent <= 4.5].sum()+(norm(y[:-1, 1]-y[1:, 0])-cross_a).square().sum()+(norm(y[:-1, 2]-y[1:, 1])-cross_b).square().sum()
        loss = loss+c['preservation_weight']*preserve/len(bb)+c['tether_weight']*shift.square().sum()/len(bb)
        optimizer.zero_grad()
        loss.backward()
        if not torch.isfinite(loss) or not torch.isfinite(shift.grad).all():
            return bb.copy(), dict(status='fallback_nonfinite', steps=step)
        optimizer.step()
        with torch.no_grad():
            shift.mul_(torch.clamp(c['max_translation']/norm(shift).clamp_min(1e-12), max=1)[:, None])
        if step >= c['check_start'] and (step-c['check_start']) % c['check_every'] == 0:
            candidate = (x+shift.detach()[:, None]).numpy().astype(bb.dtype)
            accepted, details = acceptance(bb, candidate, c)
            if accepted:
                return candidate, dict(status='repaired', steps=step, **details)
    return bb.copy(), dict(status='fallback_constraints', steps=c['steps'], last_candidate=details)
