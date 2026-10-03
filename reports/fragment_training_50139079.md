# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "53564094b5d0a0be93c9fd4bcc70857a960d976ee4212eef4c203cdc8837f001",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 940.4435592107475,
  "evaluation_seconds": 330.0151965855621,
  "elapsed_seconds": 1321.5174776380882,
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.421875,
          "joint_fraction": 0.390625,
          "mean_motif_drms": 1.2769789597950876,
          "mean_reference_ca_lddt": 0.34727190487410375,
          "mean_pairwise_sample_ca_rmsd": 16.619923923314012
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
          0.21875,
          0.5625
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.4609375,
          "joint_fraction": 0.4609375,
          "mean_motif_drms": 2.7593028721166775,
          "mean_reference_ca_lddt": 0.40147607224199255,
          "mean_pairwise_sample_ca_rmsd": 24.560649685999664
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
        "mean": 0.4609375,
        "ci95": [
          0.3125,
          0.609375
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.453125,
          "joint_fraction": 0.453125,
          "mean_motif_drms": 1.213253634981811,
          "mean_reference_ca_lddt": 0.3468341117632471,
          "mean_pairwise_sample_ca_rmsd": 16.684713543057963
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
        "mean": 0.453125,
        "ci95": [
          0.28125,
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.40625,
          "joint_fraction": 0.40625,
          "mean_motif_drms": 2.595249128062278,
          "mean_reference_ca_lddt": 0.40272005324965354,
          "mean_pairwise_sample_ca_rmsd": 24.350016687212555
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
        "mean": 0.40625,
        "ci95": [
          0.2578125,
          0.5546875
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
