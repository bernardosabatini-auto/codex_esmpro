# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50384726/manifest.json",
  "manifest_sha256": "81dbaec2666705a3f105eb120ef942cbb946bd2575cd8663a651da8c4c8bae5c",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "cca135f1402f1b149562926168fdfd48682b979ee189c02e5de11f93300fc205",
  "predictions_sha256": "4a713db15216d34ed820a03442a4194cfb9c925af7b6531dbe182b7c7dd3dfac",
  "updates": 40,
  "trainable_parameters": 9316304,
  "training_seconds": 13.822972021065652,
  "elapsed_seconds": 64.67047912813723,
  "peak_reserved_GiB": 35.80078125,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 3.7566826343536377,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      0.8417004346847534,
      0.8417004346847534
    ],
    "token_gradient_norm": 0.0011760685592889786,
    "pair_gradient_norm": 0.0005854783812537789,
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
      "mean_scaffold_rmsd": 1.1894666048471605e-14,
      "connected_raw": 3,
      "all_hidden_flank_edges_valid": 16
    },
    {
      "arm": "native_direct",
      "samples": 16,
      "raw": 16,
      "valid": 16,
      "mean_motif_rmsd": 0.08101941941320709,
      "mean_scaffold_rmsd": 1.1127324758400693e-14,
      "connected_raw": 16,
      "all_hidden_flank_edges_valid": 16
    },
    {
      "arm": "generated_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 4.478334702552212,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.798488816040345,
      "mean_scaffold_rmsd": 4.662307671447396,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 4.267004905936337,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 9.81072695941466,
      "mean_scaffold_rmsd": 4.4142868780899205,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 4.485787677320218,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_untrained",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 4.281625291011979,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Training-only fixed-scaffold bridge flow: original generated far scaffold and requested20residue motif held fixed; eight-residue flanks on each side generated. Native context is oracle-only. Every case,including15proven-obstructed generated pairs,retained. Same2000draws as wider-mask predecessor. Complete geometry/hidden-edge gate licenses separate full matched refolding only; no designability claim from imposed anchors or raw geometry.",
  "flank_context": true,
  "context_flank": 8,
  "flank_protocol_sha256": "0c6664f3c34a8e7f41c5cc2aadb6086ad5a452d1c770a14bcc6f6e75a4c9bd23",
  "junction_weighted": true,
  "junction_protocol_sha256": "8d7ffba4c347bb8ab44718a5ab9f381dae41be5ee517acfdfbda5ca844155759",
  "paired_baseline_updates": 40,
  "flank_controls": [
    {
      "kind": "zero_width",
      "arm": "generated",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "native",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "generated",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "native",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "generated",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "native",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "generated",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "zero_width",
      "arm": "native",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "generated",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "native",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "generated",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "native",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "generated",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "native",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "generated",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "max_abs": 0.0
    },
    {
      "kind": "nonleak",
      "arm": "native",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "max_abs": 0.0
    }
  ],
  "closure_summary": [
    {
      "arm": "generated_cond",
      "samples": 16,
      "coarse_valid": 0,
      "complete_geometry": 0,
      "all_hidden_flank_edges_valid": 0,
      "refold_eligible_geometry": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "coarse_valid": 0,
      "complete_geometry": 0,
      "all_hidden_flank_edges_valid": 0,
      "refold_eligible_geometry": 0
    }
  ],
  "closed_sha256": "7d3a7fc407a9ae1c5c49845c0390220b1f7efc8a79ab6b3059be942c2e195ac2",
  "cpu_closure_seconds": 21.35382288461551,
  "estimated_full_cpu_seconds": 317,
  "scaffold_bridge": true,
  "bridge_protocol_sha256": "77f616b598ccbbbace8152fdd7b95b1159b5fde5ac0cd1439e851ba49d9b6f45",
  "bridge_fixed_groups": 32,
  "bridge_fixed_max_abs_angstrom": 7.62939453125e-06,
  "bridge_runtime_calls": 50,
  "paired_wider_mask_updates": 40
}
```
