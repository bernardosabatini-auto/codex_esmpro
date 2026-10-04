# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50376770/manifest.json",
  "manifest_sha256": "075bceb62e07803bdbf6d35ea41258fa5f15ebe4aaab5acda30f732816a8ee66",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "0af5949d0d58e5443c4776afc6ed2cbfd79ec01b0165584624f11df5170ef047",
  "predictions_sha256": "b2af425e0143e03793ad16ed3811ff2396c34d1febd5c36b7f925f66fd72fd6e",
  "updates": 2000,
  "trainable_parameters": 9316304,
  "training_seconds": 698.455287868157,
  "elapsed_seconds": 778.4007712700404,
  "peak_reserved_GiB": 37.16796875,
  "controls": 192,
  "initial_controls": 72,
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
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 2.3159800953239724,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.672877820329755,
      "mean_scaffold_rmsd": 3.3475553923986476,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 2.1115552963028152,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.517202181498488,
      "mean_scaffold_rmsd": 3.3498686345293125,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 5.0387855385618305,
      "connected_raw": 0,
      "all_hidden_flank_edges_valid": 0
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 5.798644776235642,
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
          "mean": -0.1953125,
          "ci95": [
            -0.28125,
            -0.1171875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -1.0,
          "ci95": [
            -1.0,
            -1.0
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
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.672877209940971,
          "ci95": [
            -7.407131303529564,
            -6.067004528857409
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
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
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
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.517201353496188,
          "ci95": [
            -7.224742858344145,
            -5.905045737678267
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
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
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
  "scope": "Training-only eight-flank context masking with exact20residue coordinate anchors. Same2000training draws as junction-weighted baseline. Untrained wider-mask controls are new; zero-width controls reproduce historical untrained outputs. CPU closure retains original4residue correction window; require every peptide/CAedge in eight hidden flanks valid as well. Only complete128sample endpoint geometry can license matched refolds; geometry is not designability.",
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
      "coarse_valid": 0,
      "complete_geometry": 0,
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
  "closed_sha256": "b7e206f9902969d13118d8084d1550bcc2807e08641c12a5a32c53bfd08df75b",
  "cpu_closure_seconds": 154.67749898904003,
  "estimated_full_cpu_seconds": 293
}
```

Verdict: failed. The trained wider-context-mask model has0/128coarse-valid
generated outputs and0/128native-context outputs. The unchanged CPUclosure
rescues0/128pergenerated arm; none qualifies for refolding. The previous trained
model passes30/128under the same completegeometry+eight-flank-edge gate.
Paired family difference−23.44percentagepoints (95%interval−32.03to−14.84).
All2,000training draws match the junction-weighted baseline, the profile/full
first40weights match exactly, and all original/numerical controls pass.

Do not extend this checkpoint or spend on refolds. Next tests explicit fixed
far-scaffold coordinates during bridge inpainting, as prospectively defined in
`configs/fragment_scaffold_bridge_protocol.json`. Native context failure and
widespread far-scaffold damage prevent attributing this result only to
generated-context mismatch. This is an unsuccessful capacity experiment.
