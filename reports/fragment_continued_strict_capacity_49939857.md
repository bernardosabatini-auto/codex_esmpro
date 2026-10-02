# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_49929751",
      "manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
      "predictions_sha256": "714bf76ba30e37a2a9bd5474684784678eafd72488efacd3e87574a233c940a5"
    },
    {
      "run": "runs/fragment_training_49939857",
      "manifest_sha256": "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
      "predictions_sha256": "2239a8ad1ea53c9de81d9fc0aad706a0cdddf08108938ed294cf5c4815f34f2d"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49929751",
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 8,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 8.630892650400812
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 15.902482436559744
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0625,
        "ci95": [
          0.0078125,
          0.1328125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49929751",
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 4.867760111507188
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.604169354469198
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
      "run": "fragment_training_49939857",
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
    }
  ]
}
```
