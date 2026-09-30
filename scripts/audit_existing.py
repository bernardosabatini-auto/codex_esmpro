"""Reconcile existing experimental scores and inspect data; CPU only, no models."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from latentfold.data import read_ids
from latentfold.metrics import paired_comparison, wilson_interval


def fingerprint(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run(root):
    notes = root / "notes"
    manifest = notes / "exp_val_names.txt"
    ours_file = notes / "tm_last_pf_459M_p128x8_long512_scratch_sweep_named_exp_val_names.json"
    theirs_file = notes / "gate12_esmfold2_fast_expval.json"
    ids = read_ids(manifest)
    ours_json, theirs_json = (json.loads(p.read_text()) for p in (ours_file, theirs_file))
    row = ours_json["rows"]["2.0"]
    if ours_json["n"] != len(ids) or len(row["tm_per_protein"]) != len(ids) or row["coverage"] != 1:
        raise ValueError("legacy score count/coverage does not match current target manifest")
    ours = dict(zip(ids, row["tm_per_protein"], strict=True))
    theirs = {name: record["tm"] for name, record in theirs_json["per_protein"].items()}
    comparison = {"all": paired_comparison(ours, theirs)}
    for tag, predicate in (("short", lambda n: n <= 256), ("long", lambda n: n > 256)):
        selected = [n for n in ids if predicate(theirs_json["per_protein"][n]["len"])]
        comparison[tag] = paired_comparison({n: ours[n] for n in selected}, {n: theirs[n] for n in selected})
    source_h5 = root / "data/phase1_dataset/dataset_exp_val.h5"
    quality = []
    with h5py.File(source_h5, "r") as h:
        if set(ids) != set(h["val"]):
            raise ValueError("HDF5 target set differs from manifest")
        for name in ids:
            g = h["val"][name]
            ca, z = g["ca_coords"][:], g["z"][:]
            seq = g.attrs["sequence"]
            if not np.isfinite(ca).all() or not np.isfinite(z).all() or len(seq) != len(ca) or len(z) != len(ca):
                raise ValueError(f"invalid source arrays: {name}")
            lengths = np.linalg.norm(np.diff(ca, axis=0), axis=1)
            quality.append({"id": name, "length": len(seq), "ca_breaks_gt4.5A": int((lengths > 4.5).sum()),
                            "short_ca_links_lt3.3A": int((lengths < 3.3).sum()),
                            "has_residue_index_map": any(k in g for k in ("residue_index", "residue_indices", "seqidx")),
                            "latent_mean_abs_max": float(abs(z.mean(-1)).max()),
                            "latent_variance_mean": float(z.var(-1).mean())})
    designability = {}
    for fn in ("gate31_notes_gate28_real.json", "gate31_gate30_base_prior.json", "gate31_uab_u1.json", "gate31_uab_u3.json", "gate31_uab_u5.json", "gate31_uab_u10.json"):
        for name, r in json.loads((notes / fn).read_text()).items():
            success = round(r["designable_frac"] * r["n"])
            designability[name] = {**r, "successes": success, "wilson_ci95": wilson_interval(success, r["n"])}
    timing_file = notes / "gate21_inference_cost_NVIDIA_RTX_PRO_6000_Blackwell_Server_Edition.json"
    timing = json.loads(timing_file.read_text())
    return {"provenance": [fingerprint(p) for p in (manifest, ours_file, theirs_file, timing_file)],
            "legacy_identity_caveat": "Legacy score vectors omit IDs; mapping assumes the current names file is the historical order. Length and HDF5 membership were checked; historical order cannot be proved.",
            "comparison_same_run": comparison, "accuracy_steps": ours_json["steps"], "timing_steps": timing["steps"],
            "oracle_best_of_k": row["tm_best_of_k"], "oracle_k": row["k"],
            "timing": timing, "designability": designability,
            "data_quality": {"n": len(quality), "targets_with_ca_breaks": sum(r["ca_breaks_gt4.5A"] > 0 for r in quality),
                             "total_ca_breaks": sum(r["ca_breaks_gt4.5A"] for r in quality),
                             "targets_with_residue_index_map": sum(r["has_residue_index_map"] for r in quality)},
            "data_quality_per_target": quality}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("comparison_same_run", "accuracy_steps", "timing_steps", "data_quality")}, indent=2))
