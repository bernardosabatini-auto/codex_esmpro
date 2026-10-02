"""Length scheduling for an equal-protein expected flow-matching objective."""
import numpy as np


def proportional_schedule(bucket_counts, updates, seed):
    lengths=sorted(bucket_counts)
    if not lengths or type(updates) is not int or updates<1 or any(type(bucket_counts[k]) is not int or bucket_counts[k]<1 for k in lengths):
        raise ValueError('positive bucket counts and update budget required')
    counts=np.array([bucket_counts[k] for k in lengths],dtype=float)
    # With a mean loss within a bucket, P(bucket)=N_bucket/N gives each
    # protein expected coefficient 1/N before clipping and optimizer updates.
    return np.random.default_rng(seed).choice(lengths,size=updates,p=counts/counts.sum()).tolist()
