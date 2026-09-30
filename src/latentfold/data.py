"""Read inherited HDF5 files lazily without truncating or caching whole datasets."""
from pathlib import Path
import hashlib
import h5py
import numpy as np
import torch


def read_record(path, split, target_id, *, max_length=512, embedding_dim=None):
    with h5py.File(path, "r") as h:
        g = h[split][target_id]
        seq = g.attrs["sequence"]
        if isinstance(seq, bytes):
            seq = seq.decode("ascii")
        z, ca, esm = (g[k][:].astype(np.float32) for k in ("z", "ca_coords", "esm2_emb"))
    n = len(seq)
    if n < 1 or n > max_length:
        raise ValueError(f"{target_id}: length {n} outside [1, {max_length}]; no silent truncation")
    if z.shape != (n, 8) or ca.shape != (n, 3) or esm.ndim != 2 or len(esm) != n:
        raise ValueError(f"{target_id}: sequence/embedding/latent/coordinate mismatch")
    if embedding_dim is not None and esm.shape[1] != embedding_dim:
        raise ValueError(f"{target_id}: wrong embedding dimension")
    if not all(np.isfinite(v).all() for v in (z, ca, esm)):
        raise ValueError(f"{target_id}: nonfinite input")
    return {"id": target_id, "sequence": seq, "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
            "z": torch.from_numpy(z), "ca": torch.from_numpy(ca), "esm": torch.from_numpy(esm)}


def collate(records):
    if not records or len({r["id"] for r in records}) != len(records):
        raise ValueError("batch must contain unique target IDs")
    lengths = [len(r["sequence"]) for r in records]
    b, length, dim = len(records), max(lengths), records[0]["esm"].shape[1]
    result = {k: torch.zeros(b, length, width) for k, width in (("esm", dim), ("z", 8), ("ca", 3))}
    result["mask"] = torch.zeros(b, length, dtype=torch.bool)
    for i, (r, n) in enumerate(zip(records, lengths)):
        for key in ("esm", "z", "ca"):
            result[key][i, :n] = r[key]
        result["mask"][i, :n] = True
    result.update(ids=[r["id"] for r in records], lengths=lengths)
    return result


def read_ids(path):
    names = [s.strip() for s in Path(path).read_text().splitlines() if s.strip()]
    if not names or len(names) != len(set(names)):
        raise ValueError("target manifest must be nonempty and contain unique IDs")
    return names
