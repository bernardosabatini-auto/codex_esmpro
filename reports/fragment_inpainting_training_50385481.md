# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50385481/manifest.json",
  "manifest_sha256": "5daa41e153cccfe8518101aff92bc4e2c3a36bb0ad6e1d92bbd610be6ab335dc",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "3557ad12041daf1b5fd5ff45eb90486d36f33fc918b2428d9b0d2a0e79d0d5e8",
  "predictions_sha256": "92ada2b59853f85b44c1bd8b5ccf1d34193c85fc2919c1a16672fa04a4869757",
  "updates": 2000,
  "trainable_parameters": 9316304,
  "training_seconds": 690.1234160498716,
  "elapsed_seconds": 769.6168617149815,
  "peak_reserved_GiB": 37.169921875,
  "controls": 192,
  "initial_controls": 72,
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
      "connected_raw": 25,
      "all_hidden_flank_edges_valid": 128
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.4424526297461972e-14,
      "connected_raw": 127,
      "all_hidden_flank_edges_valid": 124
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 20,
      "valid": 20,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 1.621285534987924,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.71384588528066,
      "mean_scaffold_rmsd": 2.7479101300350943,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 25,
      "valid": 25,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 1.369249059528801,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.518937118756746,
      "mean_scaffold_rmsd": 2.3894637597780353,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 4.041773480268443,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 4.370682721587727,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    }
  ],
  "refold_eligibility": {
    "qualified": false,
    "eligible_complete_geometry": 0,
    "required": 45
  },
  "contrasts": [
    {
      "candidate": "generated_cond",
      "reference": "parent",
      "metrics": {
        "raw_gate_passed": {
          "mean": -0.0390625,
          "ci95": [
            -0.171875,
            0.09375
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -0.84375,
          "ci95": [
            -0.921875,
            -0.7578125
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
          "mean": 0.15625,
          "ci95": [
            0.078125,
            0.2421875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.15625,
          "ci95": [
            0.078125,
            0.2421875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.7138452748918755,
          "ci95": [
            -7.429686258129363,
            -6.1193626063307045
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
          "mean": 0.15625,
          "ci95": [
            0.078125,
            0.2421875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.15625,
          "ci95": [
            0.078125,
            0.2421875
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
          "mean": 0.1953125,
          "ci95": [
            0.1015625,
            0.296875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.1953125,
          "ci95": [
            0.1015625,
            0.296875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.518936290754445,
          "ci95": [
            -7.108181579184315,
            -5.990348296361571
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
          "mean": 0.1953125,
          "ci95": [
            0.1015625,
            0.296875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.1953125,
          "ci95": [
            0.1015625,
            0.296875
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
  "scope": "Training-only fixed-scaffold bridge flow: original generated far scaffold and requested20residue motif held fixed; eight-residue flanks on each side generated. Native context is oracle-only. Every case,including15proven-obstructed generated pairs,retained. Same2000draws as wider-mask predecessor. Complete geometry/hidden-edge gate licenses separate full matched refolding only; no designability claim from imposed anchors or raw geometry.",
  "flank_context": true,
  "context_flank": 8,
  "flank_protocol_sha256": "0c6664f3c34a8e7f41c5cc2aadb6086ad5a452d1c770a14bcc6f6e75a4c9bd23",
  "junction_weighted": true,
  "junction_protocol_sha256": "8d7ffba4c347bb8ab44718a5ab9f381dae41be5ee517acfdfbda5ca844155759",
  "paired_baseline_updates": 2000,
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
      "samples": 128,
      "coarse_valid": 29,
      "complete_geometry": 1,
      "all_hidden_flank_edges_valid": 0,
      "refold_eligible_geometry": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "coarse_valid": 0,
      "complete_geometry": 0,
      "all_hidden_flank_edges_valid": 0,
      "refold_eligible_geometry": 0
    }
  ],
  "closed_sha256": "c4e34737a3bef664b5b4ab8b900b125805ef6521d76d5d690b6ba20992a8c702",
  "cpu_closure_seconds": 155.92331524961628,
  "estimated_full_cpu_seconds": 294,
  "scaffold_bridge": true,
  "bridge_protocol_sha256": "77f616b598ccbbbace8152fdd7b95b1159b5fde5ac0cd1439e851ba49d9b6f45",
  "bridge_fixed_groups": 256,
  "bridge_fixed_max_abs_angstrom": 1.52587890625e-05,
  "bridge_runtime_calls": 330,
  "paired_wider_mask_updates": 2000
}
```
