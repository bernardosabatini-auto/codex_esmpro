# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50343189/manifest.json",
  "manifest_sha256": "48a2df4488961aa3efc191b6083fd27ca52e0fde8ffc51c217a60a74f348bd57",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "7ea94ab0a17e8f27e770745b867a4d39c86cbacb691863e66894c67632054032",
  "predictions_sha256": "eeaf0fba25c0205b12d242599e9286cd3c4d3b5502e7e2810ec118e2901ad0f5",
  "updates": 40,
  "trainable_parameters": 9316304,
  "training_seconds": 13.740793787874281,
  "elapsed_seconds": 57.5061483210884,
  "peak_reserved_GiB": 35.80078125,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 0.1679375320672989,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      0.008746504783630371,
      0.008746504783630371
    ],
    "token_gradient_norm": 3.3967244235100225e-05,
    "pair_gradient_norm": 2.8458032829803415e-05,
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
  "recommended_full_minutes": 27,
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
      "raw": 11,
      "valid": 11,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 0.33512535647563596
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.892833035820694,
      "mean_scaffold_rmsd": 0.4083449936548865
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 12,
      "valid": 12,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 0.3727229221240187
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.169616312228829,
      "mean_scaffold_rmsd": 0.5286933141506172
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "raw": 12,
      "valid": 12,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 0.3391778103746281
    },
    {
      "arm": "native_untrained",
      "samples": 16,
      "raw": 12,
      "valid": 12,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 0.3771471929463349
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Repeated training-only diagnostic. Private decoder adapted with fixed-fragment coordinate flow matching. Exact raw motif retention is imposed, not evidence of designability. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```
