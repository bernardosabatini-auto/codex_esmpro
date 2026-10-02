# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1167.0348395342007,
  "evaluation_seconds": 332.26621703850105,
  "elapsed_seconds": 1540.3554172278382,
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
          "motif_fraction_under_1A": 0.078125,
          "joint_fraction": 0.078125,
          "mean_motif_drms": 2.113869053311646,
          "mean_reference_ca_lddt": 0.3218970368512176,
          "mean_pairwise_sample_ca_rmsd": 18.06568058245439
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.549124371260405,
          "mean_reference_ca_lddt": 0.2466195675135812,
          "mean_pairwise_sample_ca_rmsd": 19.453798517361665
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.078125,
        "ci95": [
          0.015625,
          0.15625
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
          "motif_fraction_under_1A": 0.0859375,
          "joint_fraction": 0.0859375,
          "mean_motif_drms": 5.197461016708985,
          "mean_reference_ca_lddt": 0.3747627589481809,
          "mean_pairwise_sample_ca_rmsd": 23.249479662503795
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.55741659924388,
          "mean_reference_ca_lddt": 0.27065471586978995,
          "mean_pairwise_sample_ca_rmsd": 24.987527758804944
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0859375,
        "ci95": [
          0.03125,
          0.15625
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
          "mean_motif_drms": 1.641208268236369,
          "mean_reference_ca_lddt": 0.3356757846944973,
          "mean_pairwise_sample_ca_rmsd": 17.63472794411761
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.600350219756365,
          "mean_reference_ca_lddt": 0.24967050041503333,
          "mean_pairwise_sample_ca_rmsd": 19.327979565159602
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.234375,
        "ci95": [
          0.109375,
          0.390625
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
          "motif_fraction_under_1A": 0.265625,
          "joint_fraction": 0.265625,
          "mean_motif_drms": 3.7471692396793514,
          "mean_reference_ca_lddt": 0.3928150711602513,
          "mean_pairwise_sample_ca_rmsd": 22.868940710777288
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.299730192869902,
          "mean_reference_ca_lddt": 0.27642814940408844,
          "mean_pairwise_sample_ca_rmsd": 24.48063520375868
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.265625,
        "ci95": [
          0.1484375,
          0.390625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
