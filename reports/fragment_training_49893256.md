# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "755d309ff80bf2eee45e57419bca8c63cc9033ac60a5d0217a7ab8009fee086d",
  "updates": 2000,
  "audited_predictions": 1152,
  "training_seconds": 1053.967393715866,
  "evaluation_seconds": 312.6415871717036,
  "elapsed_seconds": 1412.8031711108051,
  "max_reserved_GiB": 21.744140625,
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
          "raw_valid_fraction": 0.953125,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 6.690505892038345,
          "mean_reference_ca_lddt": 0.24914399226254802,
          "mean_pairwise_sample_ca_rmsd": 19.579171213625703
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.112388364970684,
          "mean_reference_ca_lddt": 0.24784223941834166,
          "mean_pairwise_sample_ca_rmsd": 19.722692915519303
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
          "mean_motif_drms": 12.267519477754831,
          "mean_reference_ca_lddt": 0.2759247264748459,
          "mean_pairwise_sample_ca_rmsd": 23.77912365214661
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.090906370431185,
          "mean_reference_ca_lddt": 0.26948366321216666,
          "mean_pairwise_sample_ca_rmsd": 24.07668779683516
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 5.722377631813288,
          "mean_reference_ca_lddt": 0.2557026482649809,
          "mean_pairwise_sample_ca_rmsd": 17.241756471179087
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.209531173110008,
          "mean_reference_ca_lddt": 0.24995132772423506,
          "mean_pairwise_sample_ca_rmsd": 17.77133079692939
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
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.046875,
          "joint_fraction": 0.046875,
          "mean_motif_drms": 10.51468673418276,
          "mean_reference_ca_lddt": 0.31898082295209274,
          "mean_pairwise_sample_ca_rmsd": 22.60749916365589
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0078125,
          "joint_fraction": 0.0078125,
          "mean_motif_drms": 12.986195495352149,
          "mean_reference_ca_lddt": 0.2851187656215779,
          "mean_pairwise_sample_ca_rmsd": 23.439922646232535
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0390625,
        "ci95": [
          0.0,
          0.0859375
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
