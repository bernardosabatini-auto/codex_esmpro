"""Reference-free choice among already generated structure samples."""
import numpy as np


def ca_lddt_medoid(samples):
    """Choose the most mutually consistent of three CA structures.

    Each pair's similarity averages the two directed CA lDDT scores. Reference
    neighborhoods use 15 A, exclude only self pairs, and use strict error
    thresholds 0.5, 1, 2 and 4 A. Exact ties choose the first sample. No native
    structure, sequence alignment, learned confidence, or score enters choice.
    """
    xyz = np.asarray(samples, dtype=np.float64)
    if xyz.ndim != 3 or xyz.shape[0] != 3 or xyz.shape[2] != 3 or xyz.shape[1] < 3:
        raise ValueError('expected three matching CA structures (3,L,3), L >= 3')
    if not np.isfinite(xyz).all():
        raise ValueError('nonfinite sample coordinates')
    distances = np.linalg.norm(xyz[:, :, None, :] - xyz[:, None, :, :], axis=-1)
    neighborhoods = (distances < 15) & ~np.eye(xyz.shape[1], dtype=bool)[None]
    if not neighborhoods.any(axis=(1, 2)).all():
        raise ValueError('undefined CA lDDT neighborhood')
    similarity = np.eye(3)
    for i in range(3):
        for j in range(i+1, 3):
            error = np.abs(distances[i]-distances[j])
            directed = [np.mean([np.mean(error[neighborhoods[k]] < t)
                                 for t in (.5, 1, 2, 4)]) for k in (i, j)]
            similarity[i, j] = similarity[j, i] = np.mean(directed)
    confidence = (similarity.sum(axis=1)-1)/2
    return int(np.argmax(confidence)), confidence.tolist(), similarity.tolist()
