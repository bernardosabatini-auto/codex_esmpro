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
      "run": "runs/fragment_training_50127289",
      "manifest_sha256": "040a10b4efde683529f6c1af13da3e4b9776530c037d155b6afffffcd7a1508a",
      "predictions_sha256": "e755b5c2fda5d667ec874ed88a66c5b7a27df806b2e5545c423e628fa0b3d90a"
    },
    {
      "run": "runs/fragment_training_50127352",
      "manifest_sha256": "361ebc5c40259dfffe3cdc182a632f9bc62ef6f5f83eab3051a60df262e2d365",
      "predictions_sha256": "7341ad547b12f128c0b57dc3dd0b54fb7d99ccdb504ba44410732584f9394635"
    },
    {
      "run": "runs/fragment_training_50127387",
      "manifest_sha256": "8bda296baa6f9b808417d1eb543c9896334d5df790a7956789bf22ac525e6638",
      "predictions_sha256": "d396503e845c220f30f6f20331b03a144c2f41ee20ac8f769c428d71e3c04e33"
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
      "run": "fragment_training_50127289",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 32,
          "families_with_strict_success": 13,
          "mean_motif_ca_rmsd": 3.713589166694529
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.37142441040883
        }
      },
      "conditioned_minus_null": {
        "mean": 0.25,
        "ci95": [
          0.140625,
          0.375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127289",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 6,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 2.031806182822913
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.524053364167324
        }
      },
      "conditioned_minus_null": {
        "mean": 0.09375,
        "ci95": [
          0.015625,
          0.1875
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
      "run": "fragment_training_50127387",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 36,
          "families_with_strict_success": 14,
          "mean_motif_ca_rmsd": 3.571162258215603
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.028616304307974
        }
      },
      "conditioned_minus_null": {
        "mean": 0.28125,
        "ci95": [
          0.15625,
          0.421875
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127387",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 18,
          "families_with_strict_success": 9,
          "mean_motif_ca_rmsd": 1.709845243035082
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.711124071598235
        }
      },
      "conditioned_minus_null": {
        "mean": 0.28125,
        "ci95": [
          0.140625,
          0.421875
        ],
        "families": 16
      }
    }
  ]
}
```
