"""Paired fixed/free rigid-motif closure with identical objectives and bridges."""
import time
import numpy as np
import torch
from .torsion_closure import TorsionClosure
from .local_closure import distances
from .backbone_sterics import nonbonded_pairs, steric_loss


def rotation(vector):
    x, y, z = vector.unbind()
    zero = x * 0
    skew = torch.stack((zero, -z, y, z, zero, -x, -y, x, zero)).reshape(3, 3)
    return torch.matrix_exp(skew)


class MovableMotifClosure(TorsionClosure):
    def __init__(self, source, parent, start, motif_length, spec):
        super().__init__(source, parent, start, motif_length, spec)
        self.start, self.stop = start, start + motif_length
        self.motif = self.source[self.start:self.stop]
        self.center = self.motif.mean((0, 1))
        width = spec['flank_width']
        self.movable = list(range(start - width, self.stop + width))
        pairs = nonbonded_pairs(len(parent), self.movable)
        inside = (pairs // 4 >= start) & (pairs // 4 < self.stop)
        self.pairs = torch.tensor(pairs[~inside.all(axis=1)])
        flat = self.parent.reshape(-1, 3)
        self.atom_cutoffs = (flat[self.pairs[:, 0]] - flat[self.pairs[:, 1]]).norm(dim=-1).clamp_max(2.5)

    def assemble(self, delta, pose):
        if delta.shape != (self.count,) or pose.shape != (6,):
            raise ValueError('One vector of torsions and six rigid-pose parameters required')
        if not torch.isfinite(pose).all():
            raise ValueError('Finite rigid pose required')
        moved = (self.motif - self.center) @ rotation(pose[:3]).T + self.center + pose[3:]
        output = torch.cat((self.source[:self.start], moved, self.source[self.stop:]))
        errors, offset = [], 0
        for model in self.models:
            output, error = model.assemble(output, delta[offset:offset + model.n_torsions])
            errors.append(error)
            offset += model.n_torsions
        return output, torch.stack(errors)

    def loss(self, delta, pose):
        output, error = self.assemble(delta, pose)
        o = self.spec['objective']
        distance = distances(output.reshape(-1, 3), self.graph['ca_pairs'])
        parts = dict(
            endpoint=(error / o['endpoint_scale_angstrom']).square().mean(),
            clash=((self.cutoffs - distance).clamp_min(0) / o['ca_clash_scale_angstrom']).square().mean(),
            displacement=o['torsion_displacement_weight'] * delta.square().mean(),
            nonbonded=steric_loss(output, self.pairs, self.atom_cutoffs, scale=.25,
                                 editable_atoms=4 * len(self.movable)),
            motif_displacement=.01 * (output[self.start:self.stop] - self.motif).square().sum(-1).mean())
        loss = sum(parts.values())
        if not torch.isfinite(loss):
            raise FloatingPointError('Nonfinite movable-motif objective')
        return loss, parts


def canonical_inputs(source, parent, start, spec):
    solver = spec['solver']
    if solver['canonical_frame'] != 'parent_start_N_CA_C' or solver['input_grid_angstrom'] != 1e-6:
        raise ValueError('Changed numerical frame')
    origin = parent[start, 1].astype(np.float64)
    x = parent[start, 2].astype(np.float64) - origin
    x /= np.linalg.norm(x)
    y = parent[start, 0].astype(np.float64) - origin
    y -= np.dot(x, y) * x
    y /= np.linalg.norm(y)
    basis = np.stack((x, y, np.cross(x, y)), axis=1)
    grid = solver['input_grid_angstrom']
    return (np.round(((source - origin) @ basis) / grid) * grid,
            np.round(((parent - origin) @ basis) / grid) * grid, origin, basis)


def replay(source, parent, start, motif_length, spec, delta, pose, *, free_pose):
    """Replay stored parameters, preserving all uneditable source atoms bitwise."""
    cs, cp, origin, basis = canonical_inputs(source, parent, start, spec)
    problem = MovableMotifClosure(cs, cp, start, motif_length, spec)
    if not free_pose and np.any(np.asarray(pose) != 0):
        raise ValueError('Fixed-pose arm cannot move motif')
    candidate, _ = problem.assemble(torch.as_tensor(delta, dtype=torch.float64),
                                    torch.as_tensor(pose, dtype=torch.float64))
    result = source.copy()
    if not np.array_equal(source, parent):
        editable = problem.movable if free_pose else problem.graph['residues']
        result[editable] = candidate.detach().numpy()[editable] @ basis.T + origin
    return result


def close_movable_motif(source, parent, start, motif_length, spec, *, free_pose, deadline=None):
    tick = time.monotonic()
    if deadline is not None and tick > deadline:
        raise TimeoutError('Movable-motif CPU cap')
    source, parent = np.asarray(source), np.asarray(parent)
    cs, cp, origin, basis = canonical_inputs(source, parent, start, spec)
    problem = MovableMotifClosure(cs, cp, start, motif_length, spec)
    delta = torch.zeros(problem.count, dtype=torch.float64, requires_grad=True)
    pose = torch.zeros(6, dtype=torch.float64, requires_grad=free_pose)
    before = float(problem.loss(delta, pose)[0].detach())
    s = spec['solver']
    optimizer = torch.optim.LBFGS([delta, pose] if free_pose else [delta], lr=s['lr'],
        max_iter=s['max_iter'], max_eval=s['max_eval'], history_size=s['history_size'],
        tolerance_grad=s['tolerance_grad'], tolerance_change=s['tolerance_change'], line_search_fn=s['line_search_fn'])
    calls = 0
    def closure():
        nonlocal calls
        if deadline is not None and time.monotonic() > deadline:
            raise TimeoutError('Movable-motif CPU cap')
        optimizer.zero_grad(set_to_none=True)
        loss, _ = problem.loss(delta, pose)
        loss.backward()
        calls += 1
        return loss
    identical = np.array_equal(source, parent)
    if not identical:
        optimizer.step(closure)
    candidate, error = problem.assemble(delta, pose)
    loss, parts = problem.loss(delta, pose)
    result = source.copy()
    editable = problem.movable if free_pose else problem.graph['residues']
    if not identical:
        result[editable] = candidate.detach().numpy()[editable] @ basis.T + origin
    fixed = np.ones(len(source), dtype=bool)
    fixed[editable] = False
    if not np.array_equal(result[fixed], source[fixed]):
        raise ValueError('Uneditable atoms moved')
    return result, dict(seconds=time.monotonic() - tick, initial_loss=before, final_loss=float(loss.detach()),
        loss_terms={k:float(v.detach()) for k,v in parts.items()}, torsion_offsets=delta.detach().tolist(),
        pose=pose.detach().tolist(), free_pose=free_pose,
        motif_displacement_rmsd=float(np.sqrt(np.mean(np.sum((result[start:start+motif_length] - source[start:start+motif_length])**2, axis=-1)))),
        torsion_rms_degrees=float(delta.detach().square().mean().sqrt() * (180 / np.pi)),
        endpoint_rmsd_angstrom=error.detach().square().sum(-1).mean(-1).sqrt().tolist(),
        iterations=optimizer.state[delta].get('n_iter', 0), closure_calls=calls, fixed_exact=True, exact_noop=identical)
