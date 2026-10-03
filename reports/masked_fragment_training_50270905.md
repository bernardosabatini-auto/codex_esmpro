# Learned masked-fragment flow

```json
{
  "status": "complete",
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/masked_fragment_training_50270905/manifest.json",
  "manifest_sha256": "85e6b675506d8f793d500c0524eae12df6638a59658ad1a3f64966f41b566498",
  "protocol_sha256": "f61e4614f41a62c4825eaa1af45c90d0b01f3b521c0cf83833d9c58222c55dd4",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "53f2345db4003665d89042d46f5d5225fbc4429d599ec71b46073d45ff3d50df",
  "predictions_sha256": "5fcdaec5efca6e798c5908f0ca832f38da9ba0ada0fd4f17a55c34b587e2f50f",
  "updates": 2000,
  "trainable_parameters": 5080776,
  "training_seconds": 100.85263335006312,
  "elapsed_seconds": 158.90073288418353,
  "peak_reserved_GiB": 5.681640625,
  "controls": 128,
  "saved_ema_cpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 4.76837158203125e-07
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 3.5762786865234375e-07
    }
  ],
  "prefix_max_abs": 2.384185791015625e-07,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 1.2388032569484769e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.1961144712089116e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.171465257932296,
      "mean_scaffold_rmsd": 0.40640823451999475,
      "mean_scaffold_lddt": 0.9835599466666718
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.2650089912643265,
      "mean_scaffold_rmsd": 0.41108997162144434,
      "mean_scaffold_lddt": 0.984120394902904
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.156631846812,
      "mean_scaffold_rmsd": 0.4515444007260973,
      "mean_scaffold_lddt": 0.9865272057680703
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.2548858766017705,
      "mean_scaffold_rmsd": 0.47614033018190893,
      "mean_scaffold_lddt": 0.9867882315650618
    }
  ],
  "refold_gate": {
    "qualified": false,
    "checks": {
      "native_capacity": false,
      "native_validity": false,
      "generated_validity": false,
      "raw_gain_over_parent": false,
      "raw_gain_over_null": false,
      "families": false
    },
    "improved_families": 0
  },
  "scope": "Repeated training-only capacity diagnostic. Exact latent scaffold retention does not imply fixed coordinates or same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
