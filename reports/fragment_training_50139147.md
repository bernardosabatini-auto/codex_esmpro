# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "d28d0bf1c81f3f478c921e9e2f82b3a04721a8b963f2d041ab576312b00d168c",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 940.8152054888196,
  "evaluation_seconds": 330.5897803027183,
  "elapsed_seconds": 1374.9274831051007,
  "max_reserved_GiB": 20.59765625,
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.40625,
          "joint_fraction": 0.390625,
          "mean_motif_drms": 1.366819316521287,
          "mean_reference_ca_lddt": 0.32250811246455724,
          "mean_pairwise_sample_ca_rmsd": 18.81575908514084
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
        "mean": 0.390625,
        "ci95": [
          0.203125,
          0.59375
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.3984375,
          "joint_fraction": 0.3984375,
          "mean_motif_drms": 3.009240249870345,
          "mean_reference_ca_lddt": 0.38358524826259577,
          "mean_pairwise_sample_ca_rmsd": 24.83331008219927
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
        "mean": 0.3984375,
        "ci95": [
          0.265625,
          0.5390625
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
          "raw_valid_fraction": 0.9375,
          "motif_fraction_under_1A": 0.484375,
          "joint_fraction": 0.421875,
          "mean_motif_drms": 1.2901776619255543,
          "mean_reference_ca_lddt": 0.32524968163583645,
          "mean_pairwise_sample_ca_rmsd": 18.60828497843083
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
        "mean": 0.421875,
        "ci95": [
          0.234375,
          0.609375
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
          "raw_valid_fraction": 0.9375,
          "motif_fraction_under_1A": 0.3828125,
          "joint_fraction": 0.3828125,
          "mean_motif_drms": 2.7674414075445384,
          "mean_reference_ca_lddt": 0.3818713809551181,
          "mean_pairwise_sample_ca_rmsd": 24.526148068598175
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
        "mean": 0.3828125,
        "ci95": [
          0.2421875,
          0.5234375
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
