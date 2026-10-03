# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50081718",
      "manifest_sha256": "18e7e06531eac2d12020b0ac78703a2cbdddd2ad1f6d9c7b821f9e97c0a0cf16",
      "predictions_sha256": "d97c257075b382f3430136829513c79b38b0c024816e7bad372a1c356ccdbec6"
    },
    {
      "run": "runs/fragment_training_50085613",
      "manifest_sha256": "700aaf3e3fa70fb6051138eb58b4b5c994a3f458c86468fa29351df17eac89f6",
      "predictions_sha256": "1ef6b825d24b3955636eefb7b3e9f2a711dd5de71f6c78a17f275a8e6178364c"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50081718",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 32,
          "families_with_strict_success": 13,
          "mean_motif_ca_rmsd": 3.6795956780457155
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.054476229210593
        }
      },
      "conditioned_minus_null": {
        "mean": 0.25,
        "ci95": [
          0.1328125,
          0.375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50081718",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 4,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 2.2717918283053407
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.806493467415697
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0625,
        "ci95": [
          0.0,
          0.140625
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50085613",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 34,
          "families_with_strict_success": 15,
          "mean_motif_ca_rmsd": 3.704627985354949
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.08765106220082
        }
      },
      "conditioned_minus_null": {
        "mean": 0.265625,
        "ci95": [
          0.15625,
          0.390625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50085613",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 7,
          "families_with_strict_success": 6,
          "mean_motif_ca_rmsd": 2.176266325174935
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.81920551294624
        }
      },
      "conditioned_minus_null": {
        "mean": 0.109375,
        "ci95": [
          0.046875,
          0.1875
        ],
        "families": 16
      }
    }
  ]
}
```
