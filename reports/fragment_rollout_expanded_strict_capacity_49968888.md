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
      "predictions_sha256": "f9dde28dccbef78dd868897fdc9d2d9577a1af91aaf0f00296cc9b552d4282df"
    },
    {
      "run": "runs/fragment_training_49968888",
      "manifest_sha256": "6afbcdf16dba2613d5872d625bf7b8e83800a742ed852b05d05d21650a24be3a",
      "predictions_sha256": "e5d398476aee87b9395315f253143e45a0850800f09393020c48bac484d321c4"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49951202",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 7.9413784709197985
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.33708167956608
        }
      },
      "conditioned_minus_null": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.0390625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49951202",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 3.921471294047624
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.765628764034156
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
      "run": "fragment_training_49968888",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 123,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 6.460814634018152
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.300003185355273
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_49968888",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 3.363196529179675
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.741070251234767
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
