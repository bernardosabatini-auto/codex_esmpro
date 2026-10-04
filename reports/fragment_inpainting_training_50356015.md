# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50356015/manifest.json",
  "manifest_sha256": "11adad329842b99c2d627ace6c688c091c2944ff78618cf8f47fd04a75dc5d44",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "826bc79e67164a4c6ab008f41bc40176cc0d53610b6a160cb8e078dec1580ca8",
  "predictions_sha256": "41a8e035d157e003d3f9eac9df9bb1f2d3f468646956656915d4f938293ede29",
  "updates": 2000,
  "trainable_parameters": 9316304,
  "training_seconds": 687.9520244030282,
  "elapsed_seconds": 769.5160034317523,
  "peak_reserved_GiB": 37.169921875,
  "controls": 192,
  "initial_controls": 72,
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
  "prefix_max_abs": 0.0,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 9.705273561587831e-15,
      "junction_intact": 128,
      "connected_raw": 25,
      "all_flank_edges_valid": 128,
      "flank_peptide_outliers": 0,
      "flank_ca_gaps": 0
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.4424526297461972e-14,
      "junction_intact": 127,
      "connected_raw": 127,
      "all_flank_edges_valid": 127,
      "flank_peptide_outliers": 2,
      "flank_ca_gaps": 0
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 90,
      "valid": 90,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 0.18005486196480375,
      "junction_intact": 1,
      "connected_raw": 1,
      "all_flank_edges_valid": 1,
      "flank_peptide_outliers": 279,
      "flank_ca_gaps": 158
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.311250133309913,
      "mean_scaffold_rmsd": 0.28159003478804656,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 399,
      "flank_ca_gaps": 243
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 113,
      "valid": 113,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 0.2005273764385627,
      "junction_intact": 15,
      "connected_raw": 15,
      "all_flank_edges_valid": 14,
      "flank_peptide_outliers": 213,
      "flank_ca_gaps": 0
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.431746178672311,
      "mean_scaffold_rmsd": 0.3735241919352478,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 445,
      "flank_ca_gaps": 260
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "raw": 63,
      "valid": 63,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 0.3436172731084045,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 414,
      "flank_ca_gaps": 193
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "raw": 57,
      "valid": 57,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 0.4295237190898737,
      "junction_intact": 0,
      "connected_raw": 0,
      "all_flank_edges_valid": 0,
      "flank_peptide_outliers": 444,
      "flank_ca_gaps": 266
    }
  ],
  "refold_eligibility": {
    "qualified": false,
    "connected_raw": 1,
    "required": 45
  },
  "contrasts": [
    {
      "candidate": "generated_cond",
      "reference": "parent",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.5078125,
          "ci95": [
            0.3828125,
            0.6328125
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -0.296875,
          "ci95": [
            -0.4140625,
            -0.1875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -2.251628929539234,
          "ci95": [
            -2.635253812475305,
            -1.893847901238161
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "generated_cond",
      "reference": "generated_null",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.703125,
          "ci95": [
            0.5859375,
            0.8125
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.703125,
          "ci95": [
            0.5859375,
            0.8125
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.311249522921129,
          "ci95": [
            -6.837658768684327,
            -5.854564073819518
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "generated_cond",
      "reference": "generated_untrained",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.2109375,
          "ci95": [
            0.1015625,
            0.328125
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.2109375,
          "ci95": [
            0.1015625,
            0.328125
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "native_cond",
      "reference": "native_null",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.8828125,
          "ci95": [
            0.765625,
            0.96875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.8828125,
          "ci95": [
            0.765625,
            0.96875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.43174535067001,
          "ci95": [
            -6.893234585144648,
            -6.0026279284879305
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "native_cond",
      "reference": "native_untrained",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.4375,
          "ci95": [
            0.265625,
            0.6171875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.4375,
          "ci95": [
            0.265625,
            0.6171875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        }
      }
    }
  ],
  "scope": "Training-only junction-weighted fixed2000-update experiment. All original controls and untrained clamp outputs match the uniform-loss baseline exactly; every training draw is paired. Raw motif retention is imposed. Advancement requires45coarse-valid, motif-retaining backbones with intact junctions before the unchanged8-design/refold budget. Same-refold motif/global/scaffold AND junction agreement is required. Flank bond distances expose defects displaced outside the motif; geometry alone is not designability.",
  "junction_weighted": true,
  "junction_protocol_sha256": "8d7ffba4c347bb8ab44718a5ab9f381dae41be5ee517acfdfbda5ca844155759",
  "paired_baseline_updates": 2000,
  "exact_control_replays": 512,
  "baseline_manifest_sha256": "ce4ff9c7b685e76c5000dbe3116c721114551f394fe4d5c37c9bb9769e7f04a0",
  "legacy_refold_eligibility": {
    "qualified": true,
    "checks": {
      "strict_success_possible": true,
      "designability_floor_possible": true
    }
  }
}
```
