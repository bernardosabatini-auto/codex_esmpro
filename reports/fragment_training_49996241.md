# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "a933ada64e326e3bf7fd8c35f29dc44245ed0a61c02ccf624d8ea01e03066731",
  "updates": 2000,
  "total_training_updates": 2000,
  "audited_predictions": 1152,
  "training_seconds": 1168.5859965332784,
  "evaluation_seconds": 332.0919411261566,
  "elapsed_seconds": 1544.9797374429181,
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
          "mean_motif_drms": 5.951549364253879,
          "mean_reference_ca_lddt": 0.2567311573607555,
          "mean_pairwise_sample_ca_rmsd": 19.185964637253587
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.078135509043932,
          "mean_reference_ca_lddt": 0.24757304920942164,
          "mean_pairwise_sample_ca_rmsd": 19.561098314129048
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
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 11.8761096727103,
          "mean_reference_ca_lddt": 0.2856636578674169,
          "mean_pairwise_sample_ca_rmsd": 23.693932393738145
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 12.998202573508024,
          "mean_reference_ca_lddt": 0.27406353940558204,
          "mean_pairwise_sample_ca_rmsd": 23.530442317087054
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
          "mean_motif_drms": 3.564139454625547,
          "mean_reference_ca_lddt": 0.29582035258081596,
          "mean_pairwise_sample_ca_rmsd": 17.38824773587151
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.144213937222958,
          "mean_reference_ca_lddt": 0.24950299118168734,
          "mean_pairwise_sample_ca_rmsd": 17.791341799367668
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
          "motif_fraction_under_1A": 0.078125,
          "joint_fraction": 0.078125,
          "mean_motif_drms": 7.880744068650529,
          "mean_reference_ca_lddt": 0.3720122102937666,
          "mean_pairwise_sample_ca_rmsd": 22.433306808747247
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0078125,
          "joint_fraction": 0.0078125,
          "mean_motif_drms": 13.137797536794096,
          "mean_reference_ca_lddt": 0.2835068342376416,
          "mean_pairwise_sample_ca_rmsd": 23.30346956280324
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0703125,
        "ci95": [
          0.015625,
          0.140625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
