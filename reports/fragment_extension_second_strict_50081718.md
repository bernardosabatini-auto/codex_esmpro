# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50042807",
      "manifest_sha256": "83ef2500730cc7c4a11a8b5a30e0d8457e9100dc4212ff5039db53cfb5c94cfa",
      "predictions_sha256": "7e372b4c6a9052f9ea050174230820ffeb731aabf7abe42301d0bf9858831de8"
    },
    {
      "run": "runs/fragment_training_50043086",
      "manifest_sha256": "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d",
      "predictions_sha256": "dcbfacd60be57b7ebf5cdca1f9e42c9889b41d2665a3945f35f73e74d5b48d1e"
    },
    {
      "run": "runs/fragment_training_50081634",
      "manifest_sha256": "1d7f19277f9bb37a387e1989593a7d343d7c3d0e8e6070c6e04da87bcb58f54c",
      "predictions_sha256": "90e94f9e8b2ff220741ce9252601354d9354383dd7d774ba7ecdadda9fe6be8b"
    },
    {
      "run": "runs/fragment_training_50081718",
      "manifest_sha256": "18e7e06531eac2d12020b0ac78703a2cbdddd2ad1f6d9c7b821f9e97c0a0cf16",
      "predictions_sha256": "d97c257075b382f3430136829513c79b38b0c024816e7bad372a1c356ccdbec6"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50042807",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 11,
          "families_with_strict_success": 7,
          "mean_motif_ca_rmsd": 5.524886306621467
        },
        "null": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.24748445161098
        }
      },
      "conditioned_minus_null": {
        "mean": 0.0859375,
        "ci95": [
          0.0234375,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50042807",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 1,
          "families_with_strict_success": 1,
          "mean_motif_ca_rmsd": 3.004303379993088
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.676751904971988
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
    },
    {
      "run": "fragment_training_50043086",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 22,
          "families_with_strict_success": 12,
          "mean_motif_ca_rmsd": 4.189874909569411
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.061077495705835
        }
      },
      "conditioned_minus_null": {
        "mean": 0.171875,
        "ci95": [
          0.0859375,
          0.265625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50043086",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 3,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 2.4513569864330904
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.881118629223266
        }
      },
      "conditioned_minus_null": {
        "mean": 0.046875,
        "ci95": [
          0.0,
          0.09375
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50081634",
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 124,
          "strict_raw": 21,
          "families_with_strict_success": 10,
          "mean_motif_ca_rmsd": 5.129507739997864
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.124678756409445
        }
      },
      "conditioned_minus_null": {
        "mean": 0.1640625,
        "ci95": [
          0.0703125,
          0.2734375
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50081634",
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 2.8669598212250227
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.9141871885865
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
    }
  ]
}
```
