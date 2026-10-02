# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_49939857",
      "manifest_sha256": "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
      "predictions_sha256": "2239a8ad1ea53c9de81d9fc0aad706a0cdddf08108938ed294cf5c4815f34f2d"
    },
    {
      "run": "runs/fragment_training_49951202",
      "manifest_sha256": "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
      "predictions_sha256": "ad23c4e7fe0a449369fdcb0562b2bf96a57bd92f5ff075e33ab87632fc1d3a93"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49939857",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 20,
          "families_with_strict_success": 8,
          "mean_motif_ca_rmsd": 7.568709809452305
        },
        "null": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 9,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 14.882771733436705
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0859375,
        "ci95": [
          0.0234375,
          0.15625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49939857",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 5.368506846232206
        },
        "null": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.21955596523922
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
    }
  ]
}
```
