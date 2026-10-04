# Full fragment-conditioned decoder denoising

```json
{
  "status": "complete",
  "fragment_decoder_fm": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_decoder_fm_training_50298227/manifest.json",
  "manifest_sha256": "1bc56731de3109c8623dd6396dac2edbf93e131eee28d9b097e195c3cd688d22",
  "protocol_sha256": "9536ab9ff171d0713106809d678f2696ba121b09076e4eda719a5e3d45085717",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "d1940bc6b77ace6db5e248059f493421a98a1650ccb86fe1f81e35001f712b95",
  "predictions_sha256": "bb409cb0303bb1dd8917b5f489a38644451f2c7beed0521f538216da80a511d4",
  "updates": 40,
  "trainable_parameters": 9316304,
  "training_seconds": 14.520139631815255,
  "elapsed_seconds": 58.480609082151204,
  "peak_reserved_GiB": 36.5234375,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 30.829551696777344,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      1.790338397026062,
      1.790338397026062
    ],
    "token_gradient_norm": 0.029069550335407257,
    "pair_gradient_norm": 0.05989132076501846,
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
  "recommended_full_minutes": 28,
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
      "mean_motif_rmsd": 9.896447418786831,
      "mean_scaffold_rmsd": 0.42737370616185777
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.897160635489513,
      "mean_scaffold_rmsd": 0.4273807427587308
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.183300440799805,
      "mean_scaffold_rmsd": 0.5205886649338074
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.183819079776612,
      "mean_scaffold_rmsd": 0.5205721189980763
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Repeated training-only diagnostic. Full decoder adapted with coordinate flow matching. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```
