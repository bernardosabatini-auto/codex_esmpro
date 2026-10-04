# Fixed-fragment coordinate inpainting

```json
{
  "status": "complete",
  "fragment_inpainting": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_inpainting_training_50344679/manifest.json",
  "manifest_sha256": "ce4ff9c7b685e76c5000dbe3116c721114551f394fe4d5c37c9bb9769e7f04a0",
  "protocol_sha256": "b1db26b49c4e0fbef8a2f215fe68cb6bde136a4a73ceb6858ced0fa54bdeebb2",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "4f2e2d0fc96b3b280cbfe04ca074c0e4eeea94e49cc304d7727ab400317f0011",
  "predictions_sha256": "ae1da9f8ca774ec4e8b7da42e4f552fd182b3af7103ab81e92345e09980904a4",
  "updates": 2000,
  "trainable_parameters": 9316304,
  "training_seconds": 683.89598027803,
  "elapsed_seconds": 760.6243045530282,
  "peak_reserved_GiB": 37.16796875,
  "controls": 192,
  "initial_controls": 72,
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
  "prefix_max_abs": 0.0,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 9.705273561587831e-15
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.4424526297461972e-14
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 97,
      "valid": 97,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 0.16587160239670576
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 3,
      "mean_motif_rmsd": 5.913099643944568,
      "mean_scaffold_rmsd": 0.2727840644181377
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 122,
      "valid": 122,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 0.20368054120515278
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.0504314742621625,
      "mean_scaffold_rmsd": 0.35466398225534035
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "raw": 63,
      "valid": 63,
      "mean_motif_rmsd": 6.103887844472038e-07,
      "mean_scaffold_rmsd": 0.3436172731084045
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "raw": 57,
      "valid": 57,
      "mean_motif_rmsd": 8.280023009551482e-07,
      "mean_scaffold_rmsd": 0.4295237190898737
    }
  ],
  "refold_eligibility": {
    "qualified": true,
    "checks": {
      "strict_success_possible": true,
      "designability_floor_possible": true
    }
  },
  "contrasts": [
    {
      "candidate": "generated_cond",
      "reference": "parent",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.5625,
          "ci95": [
            0.4453125,
            0.671875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -0.2421875,
          "ci95": [
            -0.359375,
            -0.140625
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
          "mean": 0.7578125,
          "ci95": [
            0.640625,
            0.859375
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.734375,
          "ci95": [
            0.625,
            0.8359375
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -5.913099033555783,
          "ci95": [
            -6.392175370465516,
            -5.493813484266164
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
          "mean": 0.265625,
          "ci95": [
            0.15625,
            0.3828125
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.265625,
          "ci95": [
            0.15625,
            0.3828125
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
          "mean": 0.953125,
          "ci95": [
            0.8828125,
            1.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.953125,
          "ci95": [
            0.8828125,
            1.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -6.05043064625986,
          "ci95": [
            -6.494415896078431,
            -5.645548746553885
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
          "mean": 0.5078125,
          "ci95": [
            0.34375,
            0.671875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.5078125,
          "ci95": [
            0.34375,
            0.671875
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
  "scope": "Repeated training-only diagnostic. Private decoder adapted with fixed-fragment coordinate flow matching. Exact raw motif retention is imposed, not evidence of designability. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```

The measured whole monitored period contains729 complete one-second DCGM samples: SM86.40%, tensor0%, DRAM58.64%, GR94.72%; weighted real utilization51.44%. This excludes recorder startup and is not the dashboard24-hour statistic. The full Slurm allocation was12:56.
