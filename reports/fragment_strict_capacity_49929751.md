# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_49893256",
      "manifest_sha256": "755d309ff80bf2eee45e57419bca8c63cc9033ac60a5d0217a7ab8009fee086d",
      "predictions_sha256": "3cb8bc2615f7a93f11826d0f7a9478a24126e2ca16504cf779e5f76f86017d2e"
    },
    {
      "run": "runs/fragment_training_49929751",
      "manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
      "predictions_sha256": "714bf76ba30e37a2a9bd5474684784678eafd72488efacd3e87574a233c940a5"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49893256",
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 5,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 13.405625823557822
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 1,
          "families_with_strict_success": 1,
          "mean_motif_ca_rmsd": 15.797727693553057
        }
      },
      "conditioned_minus_null": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.0703125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49893256",
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 8.23346873353237
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.344770418339618
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
    }
  ]
}
```
