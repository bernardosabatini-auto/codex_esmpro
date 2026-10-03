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
    },
    {
      "run": "runs/fragment_training_50108001",
      "manifest_sha256": "eb3b29156894a79e6d0e1f51a407c4a752129a0be3e4632212c835b4e44a0acd",
      "predictions_sha256": "45b2f1fb4b8931025fb7cedeb44af87e85e909d5c2e18b6b91b95ec6815cd05b"
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
    },
    {
      "run": "fragment_training_50108001",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 124,
          "strict_raw": 28,
          "families_with_strict_success": 12,
          "mean_motif_ca_rmsd": 3.945864828103858
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.055645189106855
        }
      },
      "conditioned_minus_null": {
        "mean": 0.21875,
        "ci95": [
          0.109375,
          0.34375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50108001",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 5,
          "families_with_strict_success": 4,
          "mean_motif_ca_rmsd": 2.0624268792059066
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.565696525248821
        }
      },
      "conditioned_minus_null": {
        "mean": 0.078125,
        "ci95": [
          0.015625,
          0.15625
        ],
        "families": 16
      }
    }
  ]
}
```
