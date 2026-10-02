# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "c9a329b769b04d4d242e64bd0e68e1a6d2b74ff95f47f4b15c06358326c73653",
  "updates": 2000,
  "audited_predictions": 1152,
  "training_seconds": 947.9251305670477,
  "evaluation_seconds": 329.7725952109322,
  "elapsed_seconds": 1320.6890688752756,
  "max_reserved_GiB": 20.59765625,
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
          "mean_motif_drms": 5.988396506756544,
          "mean_reference_ca_lddt": 0.2611493176242241,
          "mean_pairwise_sample_ca_rmsd": 19.099471037448858
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 11.451117880642414,
          "mean_reference_ca_lddt": 0.28520666552878593,
          "mean_pairwise_sample_ca_rmsd": 23.794792929242817
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
          "mean_motif_drms": 3.1949331536889076,
          "mean_reference_ca_lddt": 0.29231344724552755,
          "mean_pairwise_sample_ca_rmsd": 18.936774906923095
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
          "mean_motif_drms": 7.216649770736694,
          "mean_reference_ca_lddt": 0.33061122308685165,
          "mean_pairwise_sample_ca_rmsd": 23.411852092983395
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
