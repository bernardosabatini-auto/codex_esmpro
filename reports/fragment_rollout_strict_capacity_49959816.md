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
      "predictions_sha256": "be5a5c67600f13b673992f03f2fd0580989e891d9f53927b0e73d72be317ceec"
    },
    {
      "run": "runs/fragment_training_49959816",
      "manifest_sha256": "d157e7e209ec5657817e94b993c9c66aab34328856000a6a40bcc38edd7df8cd",
      "predictions_sha256": "7966d65bb8a87aeac0ba893c9d899909025c55dd0b90f888def0e53eb4801a5d"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49939857",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 11,
          "families_with_strict_success": 6,
          "mean_motif_ca_rmsd": 8.26205766878139
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 15.701310431969828
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0703125,
        "ci95": [
          0.0234375,
          0.1328125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49939857",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 5.157350891246107
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.254375496150532
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
      "run": "fragment_training_49959816",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 11,
          "families_with_strict_success": 5,
          "mean_motif_ca_rmsd": 7.364974074337038
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 15.809515944985728
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0703125,
        "ci95": [
          0.015625,
          0.140625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49959816",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 4.880671757106535
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.176315607591205
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
