# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "8bda296baa6f9b808417d1eb543c9896334d5df790a7956789bf22ac525e6638",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1163.9442982939072,
  "evaluation_seconds": 332.9719128590077,
  "elapsed_seconds": 1595.948756373953,
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
          "raw_valid_fraction": 0.953125,
          "motif_fraction_under_1A": 0.46875,
          "joint_fraction": 0.421875,
          "mean_motif_drms": 1.2108764154836535,
          "mean_reference_ca_lddt": 0.32528813916552046,
          "mean_pairwise_sample_ca_rmsd": 18.75358262079117
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.309946060180664,
          "mean_reference_ca_lddt": 0.2424440045928564,
          "mean_pairwise_sample_ca_rmsd": 19.964940245236267
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
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.3984375,
          "joint_fraction": 0.3984375,
          "mean_motif_drms": 2.838984802016057,
          "mean_reference_ca_lddt": 0.38479367563974487,
          "mean_pairwise_sample_ca_rmsd": 24.8278039811984
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.250083912163973,
          "mean_reference_ca_lddt": 0.269434123242133,
          "mean_pairwise_sample_ca_rmsd": 25.539968833230517
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3984375,
        "ci95": [
          0.2578125,
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.625,
          "joint_fraction": 0.59375,
          "mean_motif_drms": 1.0374041479080915,
          "mean_reference_ca_lddt": 0.3309042827823887,
          "mean_pairwise_sample_ca_rmsd": 18.563194901326547
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.40980738401413,
          "mean_reference_ca_lddt": 0.24370485780092976,
          "mean_pairwise_sample_ca_rmsd": 19.886294363990984
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.59375,
        "ci95": [
          0.40625,
          0.765625
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
          "motif_fraction_under_1A": 0.5078125,
          "joint_fraction": 0.5,
          "mean_motif_drms": 2.4744597940007225,
          "mean_reference_ca_lddt": 0.3953410240592957,
          "mean_pairwise_sample_ca_rmsd": 24.245343052561743
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.28052556142211,
          "mean_reference_ca_lddt": 0.2674996858374246,
          "mean_pairwise_sample_ca_rmsd": 25.232189090884532
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.5,
        "ci95": [
          0.34375,
          0.6484375
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
