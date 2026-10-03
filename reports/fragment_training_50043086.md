# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d",
  "updates": 2000,
  "total_training_updates": 6000,
  "audited_predictions": 1152,
  "training_seconds": 1169.1087170457467,
  "evaluation_seconds": 331.8701108987443,
  "elapsed_seconds": 1539.3693914758042,
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
      "step": 0,
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
    },
    {
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.28125,
          "joint_fraction": 0.28125,
          "mean_motif_drms": 1.589390056207776,
          "mean_reference_ca_lddt": 0.3377913004299764,
          "mean_pairwise_sample_ca_rmsd": 17.382456088783464
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.488552052527666,
          "mean_reference_ca_lddt": 0.25264207876982103,
          "mean_pairwise_sample_ca_rmsd": 19.228809931103278
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.28125,
        "ci95": [
          0.125,
          0.4375
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.3203125,
          "joint_fraction": 0.3046875,
          "mean_motif_drms": 3.709201315883547,
          "mean_reference_ca_lddt": 0.3944171820706507,
          "mean_pairwise_sample_ca_rmsd": 22.69141127333102
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.30951970256865,
          "mean_reference_ca_lddt": 0.2783810748362896,
          "mean_pairwise_sample_ca_rmsd": 24.600040548646135
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3046875,
        "ci95": [
          0.171875,
          0.4453125
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
          "motif_fraction_under_1A": 0.3125,
          "joint_fraction": 0.296875,
          "mean_motif_drms": 1.4914270155131817,
          "mean_reference_ca_lddt": 0.332799251833676,
          "mean_pairwise_sample_ca_rmsd": 17.74305133119015
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.596949275583029,
          "mean_reference_ca_lddt": 0.2550187221901837,
          "mean_pairwise_sample_ca_rmsd": 18.558574568655914
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.296875,
        "ci95": [
          0.125,
          0.484375
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
          "motif_fraction_under_1A": 0.4375,
          "joint_fraction": 0.4296875,
          "mean_motif_drms": 2.850904241669923,
          "mean_reference_ca_lddt": 0.4094430875648414,
          "mean_pairwise_sample_ca_rmsd": 23.05949329501084
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.285800343379378,
          "mean_reference_ca_lddt": 0.2755835264187052,
          "mean_pairwise_sample_ca_rmsd": 24.33783364303818
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4296875,
        "ci95": [
          0.28125,
          0.578125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
