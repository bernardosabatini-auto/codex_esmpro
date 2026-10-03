# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "ceec00b022ed9914581a2b1357fee14cf6e3318aa11bab8f440bc4727b8ef0b9",
  "updates": 2000,
  "total_training_updates": 6000,
  "audited_predictions": 1152,
  "training_seconds": 1172.0115746222436,
  "evaluation_seconds": 332.56377218523994,
  "elapsed_seconds": 1550.7279916158877,
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
          "motif_fraction_under_1A": 0.359375,
          "joint_fraction": 0.359375,
          "mean_motif_drms": 1.4564803279936314,
          "mean_reference_ca_lddt": 0.3296658230883489,
          "mean_pairwise_sample_ca_rmsd": 18.22389786057919
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.414317477494478,
          "mean_reference_ca_lddt": 0.25178213524092485,
          "mean_pairwise_sample_ca_rmsd": 19.52534496659812
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.359375,
        "ci95": [
          0.1875,
          0.53125
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.296875,
          "joint_fraction": 0.296875,
          "mean_motif_drms": 3.688294568564743,
          "mean_reference_ca_lddt": 0.3876193010936789,
          "mean_pairwise_sample_ca_rmsd": 24.083084378216398
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.23455160856247,
          "mean_reference_ca_lddt": 0.27078818642048924,
          "mean_pairwise_sample_ca_rmsd": 25.549302354859847
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.296875,
        "ci95": [
          0.1640625,
          0.4375
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
          "motif_fraction_under_1A": 0.34375,
          "joint_fraction": 0.328125,
          "mean_motif_drms": 1.392661368008703,
          "mean_reference_ca_lddt": 0.3398575996178069,
          "mean_pairwise_sample_ca_rmsd": 17.562648791490783
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.532947737723589,
          "mean_reference_ca_lddt": 0.24750733591150886,
          "mean_pairwise_sample_ca_rmsd": 19.49901874323966
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.328125,
        "ci95": [
          0.1875,
          0.46875
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
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.3515625,
          "joint_fraction": 0.3515625,
          "mean_motif_drms": 3.2412720441352576,
          "mean_reference_ca_lddt": 0.3897035629311535,
          "mean_pairwise_sample_ca_rmsd": 23.694282353515774
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.74641322158277,
          "mean_reference_ca_lddt": 0.26865170318282,
          "mean_pairwise_sample_ca_rmsd": 26.600407123424745
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3515625,
        "ci95": [
          0.21875,
          0.4921875
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
      "step": 2000,
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
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
