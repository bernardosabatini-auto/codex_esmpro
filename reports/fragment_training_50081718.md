# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "18e7e06531eac2d12020b0ac78703a2cbdddd2ad1f6d9c7b821f9e97c0a0cf16",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1167.159271473065,
  "evaluation_seconds": 331.4924796107225,
  "elapsed_seconds": 1538.9730070200749,
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
      "step": 0,
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
    },
    {
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.359375,
          "joint_fraction": 0.359375,
          "mean_motif_drms": 1.4225326152518392,
          "mean_reference_ca_lddt": 0.3433032231315012,
          "mean_pairwise_sample_ca_rmsd": 16.987143652833517
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.231756038963795,
          "mean_reference_ca_lddt": 0.25895874226407245,
          "mean_pairwise_sample_ca_rmsd": 18.216801612572215
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
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.40625,
          "joint_fraction": 0.40625,
          "mean_motif_drms": 2.9361628068145365,
          "mean_reference_ca_lddt": 0.4195761612303277,
          "mean_pairwise_sample_ca_rmsd": 23.063030290482054
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.21799873560667,
          "mean_reference_ca_lddt": 0.27954534324535435,
          "mean_pairwise_sample_ca_rmsd": 23.861232949624963
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.40625,
        "ci95": [
          0.265625,
          0.546875
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
          "joint_fraction": 0.34375,
          "mean_motif_drms": 1.3677667137235403,
          "mean_reference_ca_lddt": 0.34257209411533013,
          "mean_pairwise_sample_ca_rmsd": 16.587044782038273
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.485072713345289,
          "mean_reference_ca_lddt": 0.2598380425753419,
          "mean_pairwise_sample_ca_rmsd": 17.702137706043438
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.34375,
        "ci95": [
          0.1875,
          0.515625
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
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.453125,
          "joint_fraction": 0.4453125,
          "mean_motif_drms": 2.556209744187072,
          "mean_reference_ca_lddt": 0.4293923887507012,
          "mean_pairwise_sample_ca_rmsd": 23.359516637649655
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.260355930775404,
          "mean_reference_ca_lddt": 0.2756961565202676,
          "mean_pairwise_sample_ca_rmsd": 24.26942495425982
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4453125,
        "ci95": [
          0.296875,
          0.59375
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
