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
      "run": "runs/fragment_training_50014625",
      "manifest_sha256": "95527548e361bcece2653a74ed9e2404bfd9a2c1bc7ef53299af98a0176b7bab",
      "predictions_sha256": "c2c85c1277ee58ae6b33994f148603a7efa555bce7e5e211e4ba696290f2f503"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49929751",
      "step": 2000,
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
      "step": 2000,
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
      "run": "fragment_training_50014625",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 6,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 8.434014851207003
        },
        "null": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 15.658855420167725
        }
      },
      "conditioned_minus_null": {
        "mean": 0.046875,
        "ci95": [
          0.0078125,
          0.09375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50014625",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 4.942117454266648
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.564468035490144
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
