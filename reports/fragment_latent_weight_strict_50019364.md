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
    }
  ]
}
```
