"""Reference-free choice among already generated structure samples."""
import numpy as np


def ca_lddt_medoid(samples, *, expected_samples=3):
    """Choose the most mutually consistent CA structure (three by default).

    Each pair's similarity averages the two directed CA lDDT scores. Reference
    neighborhoods use 15 A, exclude only self pairs, and use strict error
    thresholds 0.5, 1, 2 and 4 A. Exact ties choose the first sample. No native
    structure, sequence alignment, learned confidence, or score enters choice.
    """
    xyz = np.asarray(samples, dtype=np.float64)
    if expected_samples < 3 or xyz.ndim != 3 or xyz.shape[0] != expected_samples or xyz.shape[2] != 3 or xyz.shape[1] < 3:
        raise ValueError(f'expected {expected_samples} matching CA structures ({expected_samples},L,3), L >= 3')
    if not np.isfinite(xyz).all():
        raise ValueError('nonfinite sample coordinates')
    distances = np.linalg.norm(xyz[:, :, None, :] - xyz[:, None, :, :], axis=-1)
    neighborhoods = (distances < 15) & ~np.eye(xyz.shape[1], dtype=bool)[None]
    if not neighborhoods.any(axis=(1, 2)).all():
        raise ValueError('undefined CA lDDT neighborhood')
    similarity = np.eye(expected_samples)
    for i in range(expected_samples):
        for j in range(i+1, expected_samples):
            error = np.abs(distances[i]-distances[j])
            directed = [np.mean([np.mean(error[neighborhoods[k]] < t)
                                 for t in (.5, 1, 2, 4)]) for k in (i, j)]
            similarity[i, j] = similarity[j, i] = np.mean(directed)
    confidence = (similarity.sum(axis=1)-1)/(expected_samples-1)
    return int(np.argmax(confidence)), confidence.tolist(), similarity.tolist()
