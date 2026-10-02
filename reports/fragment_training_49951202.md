# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1162.9733714889735,
  "evaluation_seconds": 332.2207130594179,
  "elapsed_seconds": 1532.867692317348,
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
          "mean_motif_drms": 2.3216553665697575,
          "mean_reference_ca_lddt": 0.31240692295216455,
          "mean_pairwise_sample_ca_rmsd": 18.365568504078336
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.552420172840357,
          "mean_reference_ca_lddt": 0.24850526751311564,
          "mean_pairwise_sample_ca_rmsd": 19.44528059597853
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
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0703125,
          "joint_fraction": 0.0703125,
          "mean_motif_drms": 5.778174917213619,
          "mean_reference_ca_lddt": 0.3637502026589584,
          "mean_pairwise_sample_ca_rmsd": 23.272643329394974
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.550568636506796,
          "mean_reference_ca_lddt": 0.2683919964495225,
          "mean_pairwise_sample_ca_rmsd": 24.811524955380072
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.140625,
          "joint_fraction": 0.140625,
          "mean_motif_drms": 1.9615341303870082,
          "mean_reference_ca_lddt": 0.3249707329536904,
          "mean_pairwise_sample_ca_rmsd": 17.673919193629057
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.43722403049469,
          "mean_reference_ca_lddt": 0.25328429697381,
          "mean_pairwise_sample_ca_rmsd": 19.193106693109833
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.140625,
        "ci95": [
          0.03125,
          0.265625
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
          "motif_fraction_under_1A": 0.171875,
          "joint_fraction": 0.171875,
          "mean_motif_drms": 4.376887863967568,
          "mean_reference_ca_lddt": 0.3807063259797444,
          "mean_pairwise_sample_ca_rmsd": 22.972764274676006
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.371543567627668,
          "mean_reference_ca_lddt": 0.2742889593712508,
          "mean_pairwise_sample_ca_rmsd": 24.123840117842935
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.171875,
        "ci95": [
          0.09375,
          0.2578125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
