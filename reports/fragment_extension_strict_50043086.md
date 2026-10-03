# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_49951202",
      "manifest_sha256": "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
      "predictions_sha256": "ad23c4e7fe0a449369fdcb0562b2bf96a57bd92f5ff075e33ab87632fc1d3a93"
    },
    {
      "run": "runs/fragment_training_50019364",
      "manifest_sha256": "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285",
      "predictions_sha256": "d78688ca4f7c58aced0cf21e67431134f2b3a761c50ece0cbcca11e200024b97"
    },
    {
      "run": "runs/fragment_training_50042807",
      "manifest_sha256": "83ef2500730cc7c4a11a8b5a30e0d8457e9100dc4212ff5039db53cfb5c94cfa",
      "predictions_sha256": "7e372b4c6a9052f9ea050174230820ffeb731aabf7abe42301d0bf9858831de8"
    },
    {
      "run": "runs/fragment_training_50043086",
      "manifest_sha256": "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d",
      "predictions_sha256": "dcbfacd60be57b7ebf5cdca1f9e42c9889b41d2665a3945f35f73e74d5b48d1e"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49951202",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 4,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 6.366534783068611
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.15679030246862
        }
      },
      "conditioned_minus_null": {
        "mean": 0.03125,
        "ci95": [
          0.0078125,
          0.0625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49951202",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 3.3832445861056253
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.653411724516403
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50019364",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 12,
          "families_with_strict_success": 7,
          "mean_motif_ca_rmsd": 5.368250029755223
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.084763596992424
        }
      },
      "conditioned_minus_null": {
        "mean": 0.09375,
        "ci95": [
          0.03125,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50019364",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 2.7031653013876786
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.866514280942503
        }
      },
      "conditioned_minus_null": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.078125
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50042807",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 11,
          "families_with_strict_success": 7,
          "mean_motif_ca_rmsd": 5.524886306621467
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.24748445161098
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0859375,
        "ci95": [
          0.0234375,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50042807",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 1,
          "families_with_strict_success": 1,
          "mean_motif_ca_rmsd": 3.004303379993088
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.676751904971988
        }
      },
      "conditioned_minus_null": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50043086",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 22,
          "families_with_strict_success": 12,
          "mean_motif_ca_rmsd": 4.189874909569411
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.061077495705835
        }
      },
      "conditioned_minus_null": {
        "mean": 0.171875,
        "ci95": [
          0.0859375,
          0.265625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50043086",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 3,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 2.4513569864330904
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.881118629223266
        }
      },
      "conditioned_minus_null": {
        "mean": 0.046875,
        "ci95": [
          0.0,
          0.09375
        ],
        "families": 16
      }
    }
  ]
}
```
