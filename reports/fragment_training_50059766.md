# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "970cac4541cf5b317bfea08a86801a89712a3e64e7d37561906c4119f64c4297",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1157.7718324591406,
  "evaluation_seconds": 330.3664385979064,
  "elapsed_seconds": 1549.3463124651462,
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.015625,
          "joint_fraction": 0.015625,
          "mean_motif_drms": 2.8548352206125855,
          "mean_reference_ca_lddt": 0.29969867081301305,
          "mean_pairwise_sample_ca_rmsd": 17.247052787498383
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.3629706129431725,
          "mean_reference_ca_lddt": 0.2506684752691275,
          "mean_pairwise_sample_ca_rmsd": 18.037264345628582
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.046875
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
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.078125,
          "joint_fraction": 0.078125,
          "mean_motif_drms": 6.513468626886606,
          "mean_reference_ca_lddt": 0.3792607749147104,
          "mean_pairwise_sample_ca_rmsd": 22.20896078407496
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.0542116407305,
          "mean_reference_ca_lddt": 0.2821869524698294,
          "mean_pairwise_sample_ca_rmsd": 23.511301358957645
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.078125,
        "ci95": [
          0.015625,
          0.15625
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
          "motif_fraction_under_1A": 0.0625,
          "joint_fraction": 0.0625,
          "mean_motif_drms": 2.1419564429670572,
          "mean_reference_ca_lddt": 0.3184893301082996,
          "mean_pairwise_sample_ca_rmsd": 18.152621331462754
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.54604222252965,
          "mean_reference_ca_lddt": 0.246098207017488,
          "mean_pairwise_sample_ca_rmsd": 19.716075091591996
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0625,
        "ci95": [
          0.015625,
          0.125
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
          "motif_fraction_under_1A": 0.140625,
          "joint_fraction": 0.140625,
          "mean_motif_drms": 5.2359680163208395,
          "mean_reference_ca_lddt": 0.36923090265795094,
          "mean_pairwise_sample_ca_rmsd": 24.137567669742396
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.589279349893332,
          "mean_reference_ca_lddt": 0.26725892548096186,
          "mean_pairwise_sample_ca_rmsd": 25.868002012793646
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.140625,
        "ci95": [
          0.0546875,
          0.25
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
      "step": 2000,
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
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
