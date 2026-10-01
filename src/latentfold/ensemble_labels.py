"""Explicit sampling distributions for predicted structural training labels."""
import numpy as np


def label_index(arm, valid, clusters, draws):
    """Return -1 for reference, otherwise a teacher index. Never average labels.

    Three uniform draws per example allow matched RNG streams across all arms.
    Teacher arms put half their mass on the reference and half on valid teacher
    labels. No valid teacher labels implies reference-only, recorded by caller.
    Cluster balancing samples a cluster uniformly, then a member uniformly.
    """
    if arm not in ('raw_reference','reference','empirical','balanced'):
        raise ValueError('unknown label distribution')
    valid=np.asarray(valid,dtype=bool);clusters=np.asarray(clusters)
    u=np.asarray(draws)
    if valid.ndim!=1 or clusters.shape!=valid.shape or u.shape!=(3,) or not np.isfinite(u).all() or (u<0).any() or (u>=1).any():
        raise ValueError('invalid label selection inputs')
    candidates=np.flatnonzero(valid)
    if arm in ('raw_reference','reference') or u[0]<.5 or not len(candidates):return -1
    if (clusters[candidates]<0).any():raise ValueError('valid teacher sample lacks cluster')
    if arm=='balanced':
        labels=np.unique(clusters[candidates]);cluster=labels[int(u[1]*len(labels))]
        candidates=candidates[clusters[candidates]==cluster]
    return int(candidates[int(u[2]*len(candidates))])
