# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "eb3b29156894a79e6d0e1f51a407c4a752129a0be3e4632212c835b4e44a0acd",
  "updates": 2000,
  "total_training_updates": 6000,
  "audited_predictions": 1152,
  "training_seconds": 1169.107202747371,
  "evaluation_seconds": 333.1912170271389,
  "elapsed_seconds": 1548.8441906729713,
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
          "raw_valid_fraction": 0.953125,
          "motif_fraction_under_1A": 0.3125,
          "joint_fraction": 0.296875,
          "mean_motif_drms": 1.3956341007724404,
          "mean_reference_ca_lddt": 0.33813263908032404,
          "mean_pairwise_sample_ca_rmsd": 17.715432971714804
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.5265937224030495,
          "mean_reference_ca_lddt": 0.24674159668437037,
          "mean_pairwise_sample_ca_rmsd": 19.804395091323332
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.296875,
        "ci95": [
          0.15625,
          0.453125
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
          "motif_fraction_under_1A": 0.375,
          "joint_fraction": 0.375,
          "mean_motif_drms": 3.2338914594147354,
          "mean_reference_ca_lddt": 0.3898490180273993,
          "mean_pairwise_sample_ca_rmsd": 23.68498518166291
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.669898644089699,
          "mean_reference_ca_lddt": 0.26732764330769837,
          "mean_pairwise_sample_ca_rmsd": 26.47094661622505
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.375,
        "ci95": [
          0.234375,
          0.515625
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
          "mean_motif_drms": 1.2101891431957483,
          "mean_reference_ca_lddt": 0.34850291138388906,
          "mean_pairwise_sample_ca_rmsd": 16.54665935803733
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.189161282032728,
          "mean_reference_ca_lddt": 0.25217953398185133,
          "mean_pairwise_sample_ca_rmsd": 18.39281685968264
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4375,
        "ci95": [
          0.234375,
          0.640625
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.4296875,
          "joint_fraction": 0.421875,
          "mean_motif_drms": 2.679691616562195,
          "mean_reference_ca_lddt": 0.39940841956309175,
          "mean_pairwise_sample_ca_rmsd": 24.74698143739547
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.305097922682762,
          "mean_reference_ca_lddt": 0.27152560141436904,
          "mean_pairwise_sample_ca_rmsd": 25.52243607076662
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.421875,
        "ci95": [
          0.2734375,
          0.5703125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4,
  "augmentation_contrast_audit": {
    "status": "complete",
    "matched_primary_steps": 2000,
    "identical_initial_samples": 384,
    "augmented_conditional_examples": 13383,
    "all_null_targets_unchanged": true,
    "baseline_manifest_sha256": "ceec00b022ed9914581a2b1357fee14cf6e3318aa11bab8f440bc4727b8ef0b9",
    "candidate_manifest_sha256": "eb3b29156894a79e6d0e1f51a407c4a752129a0be3e4632212c835b4e44a0acd"
  }
}
```
