# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "36a9197640a1d5f7f8820ea86cee8654ccf8640b7232a7e6380ac64bc3ba2915",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1159.9960288275033,
  "evaluation_seconds": 332.1448613423854,
  "elapsed_seconds": 1536.0380971981212,
  "max_reserved_GiB": 29.177734375,
  "profile_qualified": false,
  "capacity_gate_passed": true,
  "summaries": [
    {
      "step": 0,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.453125,
          "joint_fraction": 0.4375,
          "mean_motif_drms": 1.2821911191567779,
          "mean_reference_ca_lddt": 0.34713000220268764,
          "mean_pairwise_sample_ca_rmsd": 16.65628578168792
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.20970344170928,
          "mean_reference_ca_lddt": 0.25165196272535073,
          "mean_pairwise_sample_ca_rmsd": 18.102588212241244
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4375,
        "ci95": [
          0.25,
          0.625
        ],
        "families": 16
      }
    },
    {
      "step": 0,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9609375,
          "motif_fraction_under_1A": 0.4609375,
          "joint_fraction": 0.4375,
          "mean_motif_drms": 2.681670928490348,
          "mean_reference_ca_lddt": 0.3993688983076077,
          "mean_pairwise_sample_ca_rmsd": 24.735486748972203
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.332143159583211,
          "mean_reference_ca_lddt": 0.2691645773868296,
          "mean_pairwise_sample_ca_rmsd": 25.64241734736921
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4375,
        "ci95": [
          0.2890625,
          0.5859375
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.421875,
          "joint_fraction": 0.421875,
          "mean_motif_drms": 1.2301283171400428,
          "mean_reference_ca_lddt": 0.3456057466770231,
          "mean_pairwise_sample_ca_rmsd": 16.44936160913944
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.294007312506437,
          "mean_reference_ca_lddt": 0.2555723758925105,
          "mean_pairwise_sample_ca_rmsd": 18.21801764707756
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.421875,
        "ci95": [
          0.203125,
          0.65625
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.421875,
          "joint_fraction": 0.421875,
          "mean_motif_drms": 2.613896062131971,
          "mean_reference_ca_lddt": 0.4005462651987117,
          "mean_pairwise_sample_ca_rmsd": 24.89062449888341
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.60599677823484,
          "mean_reference_ca_lddt": 0.27299625788506265,
          "mean_pairwise_sample_ca_rmsd": 26.282849438346595
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.421875,
        "ci95": [
          0.265625,
          0.578125
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.484375,
          "joint_fraction": 0.46875,
          "mean_motif_drms": 1.1786241084337234,
          "mean_reference_ca_lddt": 0.3432530907634022,
          "mean_pairwise_sample_ca_rmsd": 16.092711322082366
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.223446413874626,
          "mean_reference_ca_lddt": 0.25849803513893993,
          "mean_pairwise_sample_ca_rmsd": 17.41769547517228
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.46875,
        "ci95": [
          0.28125,
          0.65625
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.453125,
          "joint_fraction": 0.4453125,
          "mean_motif_drms": 2.421524338889867,
          "mean_reference_ca_lddt": 0.411998377281378,
          "mean_pairwise_sample_ca_rmsd": 24.557968925943364
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.559932185336947,
          "mean_reference_ca_lddt": 0.26690072170224566,
          "mean_pairwise_sample_ca_rmsd": 25.487805692409502
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4453125,
        "ci95": [
          0.2890625,
          0.6015625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
