# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "4046eaa75d48dd0fce3bbe6626827dd7433c16a2841ff3e337d74d222291634b",
  "updates": 2000,
  "audited_predictions": 1152,
  "training_seconds": 1588.2030189349316,
  "evaluation_seconds": 331.78589362092316,
  "elapsed_seconds": 1964.0463896268047,
  "max_reserved_GiB": 21.486328125,
  "profile_qualified": false,
  "capacity_gate_passed": false,
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 5.793510299175978,
          "mean_reference_ca_lddt": 0.26394150839464336,
          "mean_pairwise_sample_ca_rmsd": 18.753959822540935
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
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 11.132528997957706,
          "mean_reference_ca_lddt": 0.2903357936909842,
          "mean_pairwise_sample_ca_rmsd": 23.30147543193017
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
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 3.003804737702012,
          "mean_reference_ca_lddt": 0.29369148355574726,
          "mean_pairwise_sample_ca_rmsd": 18.640324300066062
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
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.017704332247376,
          "mean_reference_ca_lddt": 0.33545569079762283,
          "mean_pairwise_sample_ca_rmsd": 23.107761617932653
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
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
