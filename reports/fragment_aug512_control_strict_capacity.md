# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50106855",
      "manifest_sha256": "ceec00b022ed9914581a2b1357fee14cf6e3318aa11bab8f440bc4727b8ef0b9",
      "predictions_sha256": "b0679149352f828b53fa74a2b0bd1b790d33f39b029edfd22f734d29320f3934"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50106855",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 123,
          "strict_raw": 30,
          "families_with_strict_success": 12,
          "mean_motif_ca_rmsd": 3.961461399496983
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.092665916638506
        }
      },
      "conditioned_minus_null": {
        "mean": 0.234375,
        "ci95": [
          0.125,
          0.359375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50106855",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 6,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 2.124390164718436
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.615572316274847
        }
      },
      "conditioned_minus_null": {
        "mean": 0.09375,
        "ci95": [
          0.015625,
          0.203125
        ],
        "families": 16
      }
    }
  ]
}
```
