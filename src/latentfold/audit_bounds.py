"""Conservative reweighting of a complete finite-label reconstruction audit."""
import numpy as np


def teacher_priors(state, labels=16):
    indices=np.asarray(state['teacher_indices'],dtype=int);clusters=np.asarray(state['clusters'],dtype=int)
    if indices.ndim!=1 or not len(indices) or len(set(indices.tolist()))!=len(indices) or (indices<0).any() or (indices>=labels).any() or clusters.shape!=indices.shape or (clusters<0).any():raise ValueError('invalid teacher-state mapping')
    counts=np.bincount(clusters)
    if np.count_nonzero(counts)!=state['states']:raise ValueError('state count mismatch')
    empirical=np.zeros(labels);balanced=np.zeros(labels)
    empirical[indices]=1/len(indices);balanced[indices]=1/(state['states']*counts[clusters])
    return dict(empirical=empirical,balanced=balanced)


def worst_failure_mass(weights, failed_labels):
    """Maximum probability of failure when only the number of failed labels is known.

    Assign every failure to the largest remaining weight. This bound is attained
    by that assignment; it requires no guess about which labels actually failed.
    Zero-weight invalid source labels are retained in the audit label universe.
    """
    w=np.asarray(weights,dtype=float)
    if w.ndim!=1 or not len(w) or not np.isfinite(w).all() or (w<0).any() or not np.isclose(w.sum(),1,rtol=0,atol=1e-12):raise ValueError('invalid probability weights')
    if type(failed_labels) is not int or not 0<=failed_labels<=len(w):raise ValueError('invalid failure count')
    return float(np.sort(w)[::-1][:failed_labels].sum())
