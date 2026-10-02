# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "d5f2beac7d19ba5d16c76509a1b1b039a8db13523910d93da62ed086c3d16b68",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1159.6339430166408,
  "evaluation_seconds": 332.6183373904787,
  "elapsed_seconds": 1545.3618418639526,
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.046875,
          "joint_fraction": 0.046875,
          "mean_motif_drms": 2.271076229400933,
          "mean_reference_ca_lddt": 0.3130722571925958,
          "mean_pairwise_sample_ca_rmsd": 18.21883718047227
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.542113870382309,
          "mean_reference_ca_lddt": 0.24486551108011942,
          "mean_pairwise_sample_ca_rmsd": 19.534314843360182
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.046875,
        "ci95": [
          0.0,
          0.09375
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
          "motif_fraction_under_1A": 0.0703125,
          "joint_fraction": 0.0703125,
          "mean_motif_drms": 5.654690294060856,
          "mean_reference_ca_lddt": 0.36050561000857206,
          "mean_pairwise_sample_ca_rmsd": 23.813112148997686
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.463251499459147,
          "mean_reference_ca_lddt": 0.2658843472836381,
          "mean_pairwise_sample_ca_rmsd": 25.191419196344842
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0703125,
        "ci95": [
          0.015625,
          0.1328125
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
          "motif_fraction_under_1A": 0.234375,
          "joint_fraction": 0.234375,
          "mean_motif_drms": 1.7227803831920028,
          "mean_reference_ca_lddt": 0.3284321717242533,
          "mean_pairwise_sample_ca_rmsd": 17.752354681035772
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.35106011852622,
          "mean_reference_ca_lddt": 0.2525318010631814,
          "mean_pairwise_sample_ca_rmsd": 19.353888969768775
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.234375,
        "ci95": [
          0.09375,
          0.375
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
          "motif_fraction_under_1A": 0.1953125,
          "joint_fraction": 0.1953125,
          "mean_motif_drms": 4.251999533735216,
          "mean_reference_ca_lddt": 0.3789949035823284,
          "mean_pairwise_sample_ca_rmsd": 23.978502230426145
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.213371645659208,
          "mean_reference_ca_lddt": 0.26973058232471303,
          "mean_pairwise_sample_ca_rmsd": 25.31175805409193
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1953125,
        "ci95": [
          0.09375,
          0.3046875
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
