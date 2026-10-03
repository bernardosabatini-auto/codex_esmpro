# Strict raw fragment capacity

Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.

```json
{
  "status": "complete",
  "interpretation": "Post-training audit of the stricter raw criterion used by the refolding assay. Original distance-only capacity gates remain reported separately. Zero-event bootstrap intervals describe this fixed panel, not population uncertainty. No designability claim.",
  "sources": [
    {
      "run": "runs/fragment_training_50127267",
      "manifest_sha256": "36a9197640a1d5f7f8820ea86cee8654ccf8640b7232a7e6380ac64bc3ba2915",
      "predictions_sha256": "b49315731bb3b4054112f0d476b3991136fa82988d7addb128ac34e8a4386fae"
    },
    {
      "run": "runs/fragment_training_50127289",
      "manifest_sha256": "040a10b4efde683529f6c1af13da3e4b9776530c037d155b6afffffcd7a1508a",
      "predictions_sha256": "4a29f955af5af5d5dc76e77885e85c05339146d34399602a6e439d5e8ec5f86e"
    },
    {
      "run": "runs/fragment_training_50127352",
      "manifest_sha256": "361ebc5c40259dfffe3cdc182a632f9bc62ef6f5f83eab3051a60df262e2d365",
      "predictions_sha256": "e293239aa3c775ceda6ef8d1f994efcd1babcc284f47c316ce285d051af57481"
    },
    {
      "run": "runs/fragment_training_50127387",
      "manifest_sha256": "8bda296baa6f9b808417d1eb543c9896334d5df790a7956789bf22ac525e6638",
      "predictions_sha256": "e2ee7c0752386c5f86052734e029fd284ac1fe4faa9b86d90b58d186baac7763"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_50127267",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 30,
          "families_with_strict_success": 13,
          "mean_motif_ca_rmsd": 3.972852545429892
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.198005486154642
        }
      },
      "conditioned_minus_null": {
        "mean": 0.234375,
        "ci95": [
          0.125,
          0.3515625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127267",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 6,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 1.987040240125328
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.526949794853373
        }
      },
      "conditioned_minus_null": {
        "mean": 0.09375,
        "ci95": [
          0.0,
          0.203125
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50127289",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 30,
          "families_with_strict_success": 13,
          "mean_motif_ca_rmsd": 4.03289942280111
        },
        "null": {
          "samples": 128,
          "valid": 124,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.422957112064413
        }
      },
      "conditioned_minus_null": {
        "mean": 0.234375,
        "ci95": [
          0.125,
          0.3515625
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127289",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 5,
          "families_with_strict_success": 3,
          "mean_motif_ca_rmsd": 1.963206016030795
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.825308084274596
        }
      },
      "conditioned_minus_null": {
        "mean": 0.078125,
        "ci95": [
          0.0,
          0.171875
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50127352",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 26,
          "families_with_strict_success": 11,
          "mean_motif_ca_rmsd": 4.144237414580459
        },
        "null": {
          "samples": 128,
          "valid": 126,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 16.06190797978003
        }
      },
      "conditioned_minus_null": {
        "mean": 0.203125,
        "ci95": [
          0.09375,
          0.328125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127352",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 62,
          "strict_raw": 16,
          "families_with_strict_success": 8,
          "mean_motif_ca_rmsd": 1.9143671284585078
        },
        "null": {
          "samples": 64,
          "valid": 64,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.606746616883548
        }
      },
      "conditioned_minus_null": {
        "mean": 0.25,
        "ci95": [
          0.109375,
          0.40625
        ],
        "families": 16
      }
    },
    {
      "run": "fragment_training_50127387",
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "valid": 125,
          "strict_raw": 25,
          "families_with_strict_success": 11,
          "mean_motif_ca_rmsd": 4.428300690218637
        },
        "null": {
          "samples": 128,
          "valid": 127,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 15.98980750394663
        }
      },
      "conditioned_minus_null": {
        "mean": 0.1953125,
        "ci95": [
          0.09375,
          0.3125
        ],
        "families": 32
      }
    },
    {
      "run": "fragment_training_50127387",
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "valid": 61,
          "strict_raw": 14,
          "families_with_strict_success": 8,
          "mean_motif_ca_rmsd": 1.9659759727280823
        },
        "null": {
          "samples": 64,
          "valid": 63,
          "strict_raw": 0,
          "families_with_strict_success": 0,
          "mean_motif_ca_rmsd": 9.598153679965161
        }
      },
      "conditioned_minus_null": {
        "mean": 0.21875,
        "ci95": [
          0.109375,
          0.34375
        ],
        "families": 16
      }
    }
  ]
}
```
