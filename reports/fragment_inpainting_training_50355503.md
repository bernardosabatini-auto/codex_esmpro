# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50355503/manifest.json",
  "manifest_sha256": "5235870616de7d3629efa003c958a3e368690c62b74481667cb8428628a9ac3a",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "d05ed6c26950781cdda4be6046088f6967e7ba6c9368bde52883186f64c9134f",
  "predictions_sha256": "60a311819755b723a26c42eaffca7d0fbb21bfdf5df4b6802e9a64b74e9acb30",
  "updates": 40,
  "trainable_parameters": 9316304,
  "training_seconds": 13.997715348028578,
  "elapsed_seconds": 73.67521535092965,
  "peak_reserved_GiB": 35.80078125,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 0.9721734523773193,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      0.04370975121855736,
      0.04370975121855736
    ],
    "token_gradient_norm": 0.00019376297132112086,
    "pair_gradient_norm": 0.00034728404716588557,
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
      "mean_scaffold_rmsd": 1.1894666048471605e-14,
      "junction_intact": 16,
      "connected_raw": 3,
      "all_flank_edges_valid": 16,
      "flank_peptide_outliers": 0,
      "flank_ca_gaps": 0
    },
    {
      "arm": "native_direct",
      "samples": 16,
      "raw": 16,
      "valid": 16,
      "mean_motif_rmsd": 0.08101941941320709,
      "mean_scaffold_rmsd": 1.1127324758400693e-14,
      "junction_intact": 16,
      "connected_raw": 16,
      "all_flank_edges_valid": 16,
      "flank_peptide_outliers": 0,
      "flank_ca_gaps": 0
    },
    {
      "arm": "generated_cond",
      "samples": 16,
      "raw": 6,
      "valid": 6,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 0.36498594884266294,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 53,
      "flank_ca_gaps": 25
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.858654033776084,
      "mean_scaffold_rmsd": 0.40831748502621296,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 51,
      "flank_ca_gaps": 39
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 3,
      "valid": 3,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 0.4388362925585741,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 60,
      "flank_ca_gaps": 20
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.138282520129355,
      "mean_scaffold_rmsd": 0.5319785969652746,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 63,
      "flank_ca_gaps": 38
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "raw": 12,
      "valid": 12,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 0.3391778103746281,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 48,
      "flank_ca_gaps": 24
    },
    {
      "arm": "native_untrained",
      "samples": 16,
      "raw": 12,
      "valid": 12,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 0.3771471929463349,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 54,
      "flank_ca_gaps": 21
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Training-only junction-weighted fixed2000-update experiment. All original controls and untrained clamp outputs match the uniform-loss baseline exactly; every training draw is paired. Raw motif retention is imposed. Advancement requires45coarse-valid, motif-retaining backbones with intact junctions before the unchanged8-design/refold budget. Same-refold motif/global/scaffold AND junction agreement is required. Flank bond distances expose defects displaced outside the motif; geometry alone is not designability.",
  "junction_weighted": true,
  "junction_protocol_sha256": "8d7ffba4c347bb8ab44718a5ab9f381dae41be5ee517acfdfbda5ca844155759",
  "paired_baseline_updates": 40,
  "exact_control_replays": 64,
  "baseline_manifest_sha256": "ce4ff9c7b685e76c5000dbe3116c721114551f394fe4d5c37c9bb9769e7f04a0",
  "legacy_refold_eligibility": null
}
```
