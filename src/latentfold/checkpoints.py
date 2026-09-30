"""Strict loading of the two supported legacy architectures onto CPU."""
from pathlib import Path
import json
import torch
from .model import LatentFlowNet
from .pair_model import PairFlowNet


def load_legacy(path, *, trusted_pickle=False):
    """Use EMA weights for full checkpoints, with no positional-table resizing.

    Full old checkpoints may contain pickle-only optimizer/RNG objects. Set
    trusted_pickle=True only for a known local checkpoint. Never default to it.
    Model loading always occurs on CPU; execution device is a caller decision.
    """
    path = Path(path)
    state = torch.load(path, map_location="cpu", weights_only=not trusted_pickle, mmap=True)
    if "ema" in state:
        weights, arch = state["ema"], dict(state["arch"])
        kind, extra = state.get("model"), dict(state.get("extra_arch") or {})
    else:
        metadata = json.loads(Path(str(path) + ".meta.json").read_text())
        weights = state
        arch = {k: metadata[k] for k in ("d_model", "n_layers", "n_heads", "dropout", "self_cond", "d_cond", "rel_pos") if k in metadata}
        kind = metadata.get("model", "LatentFlowNet")
        extra = metadata.get("extra_arch") or {k: metadata[k] for k in ("d_pair", "n_pair_blocks", "pair_contact", "pair_dist_bins", "pair_fused") if k in metadata}
    clean = {}
    for key, value in weights.items():
        new_key = key.replace("_orig_mod.", "")
        if new_key in clean:
            raise ValueError("colliding compiled checkpoint keys")
        clean[new_key] = value
    arch["max_len"] = clean["pos.weight"].shape[0]
    if kind in ("PairFlowNet", "_Net"):
        if extra.get("recycle") or extra.get("pair_contact") or extra.get("pair_dist_bins"):
            raise ValueError("recycling/contact-conditioned checkpoints are outside this minimal core")
        for key in ("recycle", "p_rec", "rec_every"):
            extra.pop(key, None)
        model = PairFlowNet(**arch, **extra)
    elif kind == "LatentFlowNet":
        model = LatentFlowNet(**arch)
    else:
        raise ValueError(f"unsupported checkpoint architecture: {kind}")
    model.load_state_dict(clean, strict=True)
    return model.eval(), {"architecture": arch, "extra_architecture": extra, "model": kind}
