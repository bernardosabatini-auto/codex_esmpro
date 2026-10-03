# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50127267",
      "manifest_sha256": "36a9197640a1d5f7f8820ea86cee8654ccf8640b7232a7e6380ac64bc3ba2915",
      "predictions_sha256": "e6c4873593bd20b2cf2d6a6f3ca8a42987ae24784c8111821968554f2fa8cfd0"
    },
    {
      "run": "runs/fragment_training_50127352",
      "manifest_sha256": "361ebc5c40259dfffe3cdc182a632f9bc62ef6f5f83eab3051a60df262e2d365",
      "predictions_sha256": "7341ad547b12f128c0b57dc3dd0b54fb7d99ccdb504ba44410732584f9394635"
    },
    {
      "run": "runs/fragment_training_50139079",
      "manifest_sha256": "53564094b5d0a0be93c9fd4bcc70857a960d976ee4212eef4c203cdc8837f001",
      "predictions_sha256": "8bfd8c76edf6903f5ef34987faed203c517af5291fe231f639f63bb63212fbe8"
    },
    {
      "run": "runs/fragment_training_50139147",
      "manifest_sha256": "d28d0bf1c81f3f478c921e9e2f82b3a04721a8b963f2d041ab576312b00d168c",
      "predictions_sha256": "eaed6614b1f0fa114fefa6cbe7cb5c060d24968f6975bd5a22c8c81d94a03c8e"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50127267",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 37,
          "families_with_strict_success": 13,
          "mean_motif_ca_rmsd": 3.604892847225778
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.375108820703673
        }
      },
      "conditioned_minus_null": {
        "mean": 0.2890625,
        "ci95": [
          0.1640625,
          0.4296875
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127267",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 8,
          "families_with_strict_success": 6,
          "mean_motif_ca_rmsd": 1.9660586188834097
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.478329303131876
        }
      },
      "conditioned_minus_null": {
        "mean": 0.125,
        "ci95": [
          0.046875,
          0.21875
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50127352",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 40,
          "families_with_strict_success": 15,
          "mean_motif_ca_rmsd": 3.328930068365055
        },
        "null": {
          "samples": 128,
          "valid": 124,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.019124418658727
        }
      },
      "conditioned_minus_null": {
        "mean": 0.3125,
        "ci95": [
          0.1796875,
          0.453125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127352",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 20,
          "families_with_strict_success": 9,
          "mean_motif_ca_rmsd": 1.6662226598602112
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.653402148738477
        }
      },
      "conditioned_minus_null": {
        "mean": 0.3125,
        "ci95": [
          0.171875,
          0.46875
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50139079",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 30,
          "families_with_strict_success": 12,
          "mean_motif_ca_rmsd": 3.6795937577616686
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.092665916638506
        }
      },
      "conditioned_minus_null": {
        "mean": 0.234375,
        "ci95": [
          0.125,
          0.359375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50139079",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 7,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 2.016282851053563
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.615572316274847
        }
      },
      "conditioned_minus_null": {
        "mean": 0.109375,
        "ci95": [
          0.0,
          0.234375
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50139147",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 120,
          "strict_raw": 18,
          "families_with_strict_success": 10,
          "mean_motif_ca_rmsd": 4.3604455489228755
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.092665916638506
        }
      },
      "conditioned_minus_null": {
        "mean": 0.140625,
        "ci95": [
          0.0625,
          0.2265625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50139147",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 60,
          "strict_raw": 8,
          "families_with_strict_success": 5,
          "mean_motif_ca_rmsd": 2.108549892892057
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.615572316274847
        }
      },
      "conditioned_minus_null": {
        "mean": 0.125,
        "ci95": [
          0.03125,
          0.21875
        ],
        "families": 16
      }
    }
  ]
}
```
