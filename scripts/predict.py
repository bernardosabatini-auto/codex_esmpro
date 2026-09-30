"""Predict from cached embeddings using frozen legacy weights. CPU by default.

    Writes one NPZ per target/sample containing latent and CA/backbone coordinates,
    plus a run manifest. CUDA requires --allow-gpu and explicit user permission.
    Timing covers cached-embedding flow+decoder only, not end-to-end sequence folding.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
import torch
import numpy as np
from latentfold.checkpoints import load_legacy
from latentfold.data import read_ids, read_record, collate
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig, sample, target_noise


def file_identity(path, *, hash_contents=False):
    path = path.resolve()
    stat = path.stat()
    result = {"path": str(path), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    if hash_contents:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
        result["sha256"] = digest.hexdigest()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--h5", type=Path, required=True)
    p.add_argument("--ids", type=Path, required=True)
    p.add_argument("--split", default="val")
    p.add_argument("--proteinae-checkout", type=Path, required=True)
    p.add_argument("--proteinae-checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--guidance", type=float, default=2.0)
    p.add_argument("--decoder-steps", type=int, default=3)
    p.add_argument("--samples", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--allow-gpu", action="store_true")
    p.add_argument("--trusted-legacy-pickle", action="store_true")
    a = p.parse_args()
    if a.device == "cuda" and not a.allow_gpu:
        p.error("GPU execution requires explicit user permission and --allow-gpu")
    if a.samples < 1:
        p.error("--samples must be positive")
    if a.output.exists():
        p.error("output directory must be new")
    cfg = SampleConfig(steps=a.steps, guidance=a.guidance)
    ids = read_ids(a.ids)
    torch.set_num_threads(2)
    net, arch = load_legacy(a.checkpoint, trusted_pickle=a.trusted_legacy_pickle)
    decoder = load_proteinae(a.proteinae_checkout, a.proteinae_checkpoint, steps=a.decoder_steps)
    net, decoder = net.to(a.device), decoder.to(a.device)
    # Refuse to mix an old run with a new run.
    a.output.mkdir(parents=True, exist_ok=False)
    manifest = {"arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()},
                "sampler": asdict(cfg), "architecture": arch, "torch": torch.__version__,
                "checkpoint": file_identity(a.checkpoint, hash_contents=True),
                "decoder_checkpoint": file_identity(a.proteinae_checkpoint, hash_contents=True),
                "dataset": file_identity(a.h5),
                "ids_sha256": hashlib.sha256(a.ids.read_bytes()).hexdigest(),
                "timing_scope": "cached embeddings to decoded backbone, CPU fp32 / CUDA bf16 autocast, batch 1; not a benchmark",
                "status": "running", "records": []}
    def save():
        temp = a.output / "manifest.tmp"
        temp.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
        temp.replace(a.output / "manifest.json")
    save()
    try:
        for name in ids:
            r = read_record(a.h5, a.split, name, max_length=net.pos.num_embeddings,
                            embedding_dim=net.cond_norm.normalized_shape[0])
            batch = collate([r])
            esm, mask = batch["esm"].to(a.device), batch["mask"].to(a.device)
            n = batch["lengths"][0]
            for k in range(a.samples):
                noise = target_noise([name], [n], 8, seed=a.seed, sample_index=k, device=a.device)
                dn = target_noise([name], [4*n], 3, seed=a.seed, sample_index=k, stream="decoder", device=a.device) * decoder.fm.scale_ref
                if a.device == "cuda":
                    torch.cuda.synchronize()
                start = time.perf_counter()
                with torch.no_grad(), torch.autocast(device_type=a.device, dtype=torch.bfloat16, enabled=a.device == "cuda"):
                    z = sample(net, esm, mask, cfg, noise=noise)
                    ca, bb = decoder(z, mask, return_backbone=True, noise=dn)
                if a.device == "cuda":
                    torch.cuda.synchronize()
                elapsed = time.perf_counter() - start
                if not torch.isfinite(bb).all():
                    raise FloatingPointError(f"nonfinite decoded backbone: {name}")
                # Hashed filename supports arbitrary target IDs without path traversal.
                filename = f"{hashlib.sha256(name.encode()).hexdigest()[:20]}_{k}.npz"
                np.savez_compressed(a.output / filename, z=z[0].cpu().numpy(), ca=ca[0].cpu().numpy(), backbone=bb[0].cpu().numpy())
                manifest["records"].append({"target_id": name, "sample": k, "sequence_sha256": r["sequence_sha256"],
                                            "length": n, "file": filename, "seconds": elapsed})
                save()
        manifest["status"] = "complete"
    except BaseException as error:
        manifest["status"], manifest["error"] = "failed", f"{type(error).__name__}: {error}"
        raise
    finally:
        save()


if __name__ == "__main__":
    main()
