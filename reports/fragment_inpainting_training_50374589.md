# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50374589/manifest.json",
  "manifest_sha256": "8c929dd396df82b9ea044799121737c6ef783040c9a764fd3a1903570eea96ac",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "4764ef4e1a1b3a484da58169f18d490f6f347dd60b2d25abdc1c62fb923a0e6a",
  "predictions_sha256": "1c9dab88ef9385bf69ab96144bbb3336bf845e88146830db356a993ef5474710",
  "updates": 40,
  "trainable_parameters": 9316304,
  "training_seconds": 13.911367706023157,
  "elapsed_seconds": 58.16867104684934,
  "peak_reserved_GiB": 35.80078125,
  "controls": 24,
  "initial_controls": 16,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 23.16767120361328,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      1.5966182947158813,
      1.5966182947158813
    ],
    "token_gradient_norm": 0.005345167126506567,
    "pair_gradient_norm": 0.002850827295333147,
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
      "mean_scaffold_rmsd": 5.315291267227654,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.181820980641092,
      "mean_scaffold_rmsd": 5.251454731224923,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 5.354022834997891,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.226424181425648,
      "mean_scaffold_rmsd": 4.869811369036366,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.791887779246059e-07,
      "mean_scaffold_rmsd": 5.349006344206773,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_untrained",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 7.183440055857217e-07,
      "mean_scaffold_rmsd": 5.401742308718755,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    }
  ],
  "refold_eligibility": null,
  "contrasts": [],
  "scope": "Training-only eight-flank context masking with exact20residue coordinate anchors. Same2000training draws as junction-weighted baseline. Untrained wider-mask controls are new; zero-width controls reproduce historical untrained outputs. CPU closure retains original4residue correction window; require every peptide/CAedge in eight hidden flanks valid as well. Only complete128sample endpoint geometry can license matched refolds; geometry is not designability.",
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
  "closed_sha256": "32b20a9064c276655d454ec50d0e9d7cbb7f12cff8b5177b2b587caae90e1a37",
  "cpu_closure_seconds": 20.897016980452463,
  "estimated_full_cpu_seconds": 311
}
```
