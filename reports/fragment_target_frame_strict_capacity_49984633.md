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
      "run": "runs/fragment_training_49984633",
      "manifest_sha256": "c51d7da4bb8b86ad6691706ba56f5b14599c0a3db1ffaaf28e6d1768d0b00fd8",
      "predictions_sha256": "ac47c2c7b73c52db7b597f74910fa36304aa6ed8279fc1f357731416949ef357"
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
      "run": "fragment_training_49984633",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 114,
          "strict_raw": 7,
          "families_with_strict_success": 6,
          "mean_motif_ca_rmsd": 3.4663011165303548
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 15.597979009162605
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0546875,
        "ci95": [
          0.015625,
          0.1015625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49984633",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 1,
          "families_with_strict_success": 1,
          "mean_motif_ca_rmsd": 2.1833916550148795
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.488426280396855
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
    }
  ]
}
```
