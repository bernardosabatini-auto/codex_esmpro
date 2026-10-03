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
      "run": "runs/fragment_training_49985054",
      "manifest_sha256": "d5f2beac7d19ba5d16c76509a1b1b039a8db13523910d93da62ed086c3d16b68",
      "predictions_sha256": "06dbd489511349591fa747550911e474c1e4d8f6ac8764ae9cd8c5a47104230a"
    },
    {
      "run": "runs/fragment_training_50059766",
      "manifest_sha256": "970cac4541cf5b317bfea08a86801a89712a3e64e7d37561906c4119f64c4297",
      "predictions_sha256": "85aea0b3bca4372366eea9c933e59dc96f04e38641d11f0ae496d2dc56903df5"
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
      "run": "fragment_training_49985054",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 3,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 5.965433894012258
        },
        "null": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.03760197212495
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0234375,
        "ci95": [
          0.0,
          0.046875
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49985054",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 1,
          "families_with_strict_success": 1,
          "mean_motif_ca_rmsd": 2.817724664098182
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.63680902321359
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
      "run": "fragment_training_50059766",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 9,
          "families_with_strict_success": 7,
          "mean_motif_ca_rmsd": 5.225274163211747
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.01556912205568
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0703125,
        "ci95": [
          0.0234375,
          0.125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50059766",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 3,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 2.3053446869694323
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.676956355652706
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
