"""Strict, ID-keyed comparison and residue-corresponding geometry metrics."""
import math
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np


def paired_comparison(ours, theirs, *, clusters=None, seed=0, bootstrap=10000):
    if not ours or set(ours) != set(theirs):
        raise ValueError("paired comparison requires identical, nonempty target sets")
    names = sorted(ours)
    a, b = (np.asarray([scores[n] for n in names], dtype=float) for scores in (ours, theirs))
    if not np.isfinite(a).all() or not np.isfinite(b).all() or ((a < 0) | (a > 1) | (b < 0) | (b > 1)).any():
        raise ValueError("TM scores must all be finite and in [0,1]")
    if type(bootstrap) is not int or bootstrap < 1:
        raise ValueError("bootstrap must be positive")
    if clusters is not None and set(clusters) != set(names):
        raise ValueError("each target must have a cluster ID")
    groups = {}
    for i, name in enumerate(names):
        groups.setdefault(clusters[name] if clusters is not None else name, []).append(i)
    delta = b - a
    # Resample independent clusters, preserving the target-weighted estimand.
    sums = np.array([delta[idx].sum() for idx in groups.values()])
    counts = np.array([len(idx) for idx in groups.values()])
    rng = np.random.default_rng(seed)
    draws = np.empty(bootstrap)
    for start in range(0, bootstrap, 256):
        idx = rng.integers(len(groups), size=(min(256, bootstrap - start), len(groups)))
        draws[start:start + len(idx)] = sums[idx].sum(1) / counts[idx].sum(1)
    return {"n": len(names), "clusters": len(groups), "bootstrap_unit": "cluster" if clusters else "target",
            "ours": float(a.mean()), "theirs": float(b.mean()), "theirs_minus_ours": float(delta.mean()),
            "ci95": np.quantile(draws, [0.025, 0.975]).tolist(),
            "ours_wins": int((delta < 0).sum()), "ties": int((delta == 0).sum()), "coverage": 1.0}


def wilson_interval(successes, total):
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("invalid binomial counts")
    z, p = 1.959963984540054, successes / total
    denom = 1 + z*z / total
    center = (p + z*z / (2*total)) / denom
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denom
    return [center-half, center+half]


def _coordinates(pred, ref):
    p, q = np.asarray(pred, dtype=float), np.asarray(ref, dtype=float)
    if p.shape != q.shape or p.ndim != 2 or p.shape[1] != 3 or len(p) < 3:
        raise ValueError("expected matching coordinates (N,3), N >= 3")
    if not np.isfinite(p).all() or not np.isfinite(q).all():
        raise ValueError("coordinates must be finite")
    return p, q


def ca_metrics(pred, ref):
    """Kabsch RMSD and CA lDDT with fixed correspondence. No sequence realignment.

    The TM-shaped score here uses RMSD-optimal superposition, so is deliberately
    named tm_after_kabsch. It is NOT the optimized TM-score used for headlines.
    """
    p, q = _coordinates(pred, ref)
    pc, qc = p - p.mean(0), q - q.mean(0)
    u, _, vt = np.linalg.svd(pc.T @ qc)
    rot = u @ np.diag([1, 1, np.linalg.det(u @ vt)]) @ vt
    distances = np.linalg.norm(pc @ rot - qc, axis=-1)
    d0 = max(0.5, 1.24 * (max(len(p), 19) - 15)**(1/3) - 1.8)
    dp = np.linalg.norm(p[:, None] - p[None, :], axis=-1)
    dq = np.linalg.norm(q[:, None] - q[None, :], axis=-1)
    eligible = (dq < 15) & ~np.eye(len(p), dtype=bool)
    errors = np.abs(dp - dq)[eligible]
    lddt = float(np.mean([np.mean(errors < t) for t in (0.5, 1, 2, 4)])) if errors.size else None
    return {"ca_rmsd": float(np.sqrt(np.mean(distances**2))),
            "tm_after_kabsch": float(np.mean(1/(1+(distances/d0)**2))), "ca_lddt": lddt}


def usalign_fixed_tm(binary, predicted_pdb, reference_pdb):
    """Reference-normalized TM optimized with fixed PDB residue numbering.

    Caller must provide single chains with matching residue IDs. US-align's
    -TMscore 1 (alias -byresi 1) fixes correspondence; it does not find a new
    structural alignment. This function never falls back to another metric.
    """
    result = subprocess.run([str(binary), str(predicted_pdb), str(reference_pdb), "-TMscore", "1"],
                            check=True, capture_output=True, text=True, timeout=120)
    lines = [line for line in result.stdout.splitlines()
             if line.startswith("TM-score=") or line.startswith("TM-score =")]
    values = []
    for line in lines:
        if re.search(r"(?:Chain|Structure)[_ ]2", line):
            match = re.search(r"TM-score\s*=\s*([0-9.eE+-]+)", line)
            if match:
                values.append(float(match.group(1)))
    if len(values) != 1 or not 0 <= values[0] <= 1:
        raise ValueError("missing or ambiguous reference-normalized US-align TM-score")
    return values[0]


def usalign_coordinates(binary, pred, ref):
    """TM-optimal superposition with fixed observed-residue correspondence.

    Temporary CA-only files use the same residue numbers in both structures.
    ALA names are placeholders; -TMscore 1 uses indices, not sequence alignment.
    Missing original residue maps cannot be reconstructed from cached coordinates.
    """
    pred, ref = _coordinates(pred, ref)
    if len(pred) > 9999 or max(np.abs(pred).max(), np.abs(ref).max()) >= 999:
        raise ValueError('coordinates exceed conservative PDB formatting limits')
    with tempfile.TemporaryDirectory(prefix='latentfold_tm_') as tmp:
        paths = [Path(tmp)/'pred.pdb', Path(tmp)/'ref.pdb']
        for path, coords in zip(paths, (pred, ref)):
            with path.open('w') as handle:
                for i, (x, y, z) in enumerate(coords, 1):
                    handle.write(f'ATOM  {i:5d}  CA  ALA A{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n')
                handle.write('TER\nEND\n')
        return usalign_fixed_tm(binary, *paths)
