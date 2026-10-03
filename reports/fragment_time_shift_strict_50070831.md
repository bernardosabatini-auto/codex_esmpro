# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50019364",
      "manifest_sha256": "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285",
      "predictions_sha256": "d78688ca4f7c58aced0cf21e67431134f2b3a761c50ece0cbcca11e200024b97"
    },
    {
      "run": "runs/fragment_training_50070831",
      "manifest_sha256": "09d6392e659cbc885f7cfec0f227c03a8d10493f826962bd96012b243681ede6",
      "predictions_sha256": "6f43e94d6d614270bb34ba760656d9ac8b59f929f70877c234d6dd64e4946e4e"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50019364",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 12,
          "families_with_strict_success": 7,
          "mean_motif_ca_rmsd": 5.368250029755223
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.084763596992424
        }
      },
      "conditioned_minus_null": {
        "mean": 0.09375,
        "ci95": [
          0.03125,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50019364",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 2.7031653013876786
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.866514280942503
        }
      },
      "conditioned_minus_null": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.078125
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50070831",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 128,
          "strict_raw": 2,
          "families_with_strict_success": 2,
          "mean_motif_ca_rmsd": 5.048958388022388
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.09211854754079
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
      "run": "fragment_training_50070831",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 2.943624147427899
        },
        "null": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.780840255078875
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
