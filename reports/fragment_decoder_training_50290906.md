# Explicit fragment-conditioned coordinate decoder

```json
{
  "status": "complete",
  "fragment_decoder": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_decoder_training_50290906/manifest.json",
  "manifest_sha256": "87789916763bfdb649790ba974e4d5fac92849bef9ef0e8099314e8be5d93087",
  "protocol_sha256": "3441d5c292c095672e8975ce8aa5ee4f25feb36464a5fa96498c2876e94c86bb",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "1bda11b71e7cab3f6aa692c502ac4a333e1d95a1506dbf5c5b169a695654e86a",
  "predictions_sha256": "b69f53a5f365a718211c93cbd1f0d597e3d91a5aa0f112c7c30029b333d169d7",
  "updates": 40,
  "trainable_parameters": 82944,
  "training_seconds": 16.556275814771652,
  "elapsed_seconds": 60.16996469674632,
  "peak_reserved_GiB": 8.328125,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      180.27459716796875,
      180.27459716796875
    ],
    "token_gradient_norm": 2.9071974754333496,
    "pair_gradient_norm": 6.739734172821045,
    "prediction_tolerance_ratio": 0.0,
    "gradient_tolerance_ratio": 0.0
  },
  "saved_ema_gpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "backbone_max_abs": 0.0
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "backbone_max_abs": 0.0
    }
  ],
  "prefix_max_abs": null,
  "recommended_full_minutes": 30,
  "summary": [
    {
      "arm": "parent",
      "samples": 16,
      "raw": 3,
      "valid": 16,
      "mean_motif_rmsd": 2.119737115628963,
      "mean_scaffold_rmsd": 1.1894666048471605e-14
    },
    {
      "arm": "native_direct",
      "samples": 16,
      "raw": 16,
      "valid": 16,
      "mean_motif_rmsd": 0.08101941941320709,
      "mean_scaffold_rmsd": 1.1127324758400693e-14
    },
    {
      "arm": "generated_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.844241076590501,
      "mean_scaffold_rmsd": 0.38144332056591845
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.846506737831822,
      "mean_scaffold_rmsd": 0.38143851267154044
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.143901626448793,
      "mean_scaffold_rmsd": 0.47481730773216446
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.146152412728224,
      "mean_scaffold_rmsd": 0.4748431346212729
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Repeated training-only diagnostic. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```
