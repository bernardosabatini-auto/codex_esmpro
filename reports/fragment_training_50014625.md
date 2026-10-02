# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "95527548e361bcece2653a74ed9e2404bfd9a2c1bc7ef53299af98a0176b7bab",
  "updates": 2000,
  "total_training_updates": 2000,
  "audited_predictions": 1152,
  "training_seconds": 1168.817632376682,
  "evaluation_seconds": 330.5596168683842,
  "elapsed_seconds": 1541.241100570187,
  "max_reserved_GiB": 29.181640625,
  "profile_qualified": false,
  "capacity_gate_passed": true,
  "summaries": [
    {
      "step": 0,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.328055743128061,
          "mean_reference_ca_lddt": 0.24397619939943438,
          "mean_pairwise_sample_ca_rmsd": 19.318124828522
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.328055743128061,
          "mean_reference_ca_lddt": 0.24397619939943438,
          "mean_pairwise_sample_ca_rmsd": 19.318124828522
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.41431232728064,
          "mean_reference_ca_lddt": 0.26091556014356776,
          "mean_pairwise_sample_ca_rmsd": 24.45708333915183
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.41431232728064,
          "mean_reference_ca_lddt": 0.26091556014356776,
          "mean_pairwise_sample_ca_rmsd": 24.45708333915183
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 5.296535534784198,
          "mean_reference_ca_lddt": 0.2616649112174879,
          "mean_pairwise_sample_ca_rmsd": 19.396361532852318
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.1871435940265656,
          "mean_reference_ca_lddt": 0.24615942032732308,
          "mean_pairwise_sample_ca_rmsd": 19.65704176986477
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 10.010486510582268,
          "mean_reference_ca_lddt": 0.29810935570694025,
          "mean_pairwise_sample_ca_rmsd": 23.143071114524144
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.045212350785732,
          "mean_reference_ca_lddt": 0.27203723669174945,
          "mean_pairwise_sample_ca_rmsd": 23.615529997143852
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
          "motif_fraction_under_1A": 0.015625,
          "joint_fraction": 0.015625,
          "mean_motif_drms": 2.8677949281409383,
          "mean_reference_ca_lddt": 0.2957479707125181,
          "mean_pairwise_sample_ca_rmsd": 17.005115180875695
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.408384084701538,
          "mean_reference_ca_lddt": 0.2505344671278371,
          "mean_pairwise_sample_ca_rmsd": 18.09848855345156
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
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0703125,
          "joint_fraction": 0.0703125,
          "mean_motif_drms": 6.136612959206104,
          "mean_reference_ca_lddt": 0.38548403990858204,
          "mean_pairwise_sample_ca_rmsd": 22.0883736354509
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0078125,
          "joint_fraction": 0.0078125,
          "mean_motif_drms": 12.873956478666514,
          "mean_reference_ca_lddt": 0.2856069492243885,
          "mean_pairwise_sample_ca_rmsd": 23.185300612752982
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0625,
        "ci95": [
          0.015625,
          0.125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
