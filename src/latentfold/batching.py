"""Length-bucketed requests with reproducible noise for independent samples."""
import torch
from torch.nn import functional as F
from .data import collate
from .flow import target_noise


def requests_by_bucket(records, lengths, samples):
    if samples < 1 or not lengths or len(set(lengths)) != len(lengths):
        raise ValueError("invalid buckets or sample count")
    if len({r['id'] for r in records}) != len(records):
        raise ValueError("duplicate target IDs")
    buckets = {n: [] for n in sorted(lengths)}
    for record in sorted(records, key=lambda r: (len(r['sequence']), r['id'])):
        fits = [n for n in buckets if len(record['sequence']) <= n]
        if not fits:
            raise ValueError(f"no length bucket for {record['id']}")
        for k in range(samples):
            buckets[fits[0]].append((record, k))
    return buckets


def prediction_batch(requests, length, *, seed, decoder_scale):
    identities = [(r['id'], k) for r, k in requests]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate target/sample request")
    records = [dict(r, id=str(i)) for i, (r, _) in enumerate(requests)]
    batch = collate(records)
    delta = length - batch['esm'].shape[1]
    if delta < 0:
        raise ValueError("bucket too short")
    batch['esm'] = F.pad(batch['esm'], (0, 0, 0, delta))
    batch['mask'] = F.pad(batch['mask'], (0, delta))
    noise = torch.zeros(len(requests), length, 8)
    decoder_noise = torch.zeros(len(requests), 4*length, 3)
    for i, ((r, k), n) in enumerate(zip(requests, batch['lengths'])):
        noise[i, :n] = target_noise([r['id']], [n], 8, seed=seed, sample_index=k)[0]
        decoder_noise[i, :4*n] = target_noise([r['id']], [4*n], 3, seed=seed,
                                             sample_index=k, stream='decoder')[0] * decoder_scale
    return batch['esm'], batch['mask'], noise, decoder_noise
