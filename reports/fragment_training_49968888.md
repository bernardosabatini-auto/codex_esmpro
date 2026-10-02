# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "6afbcdf16dba2613d5872d625bf7b8e83800a742ed852b05d05d21650a24be3a",
  "updates": 500,
  "total_training_updates": 2500,
  "audited_predictions": 768,
  "training_seconds": 2635.6457317457534,
  "evaluation_seconds": 221.70361304329708,
  "elapsed_seconds": 2901.1418933765963,
  "max_reserved_GiB": 30.01171875,
  "profile_qualified": false,
  "capacity_gate_passed": null,
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
          "mean_motif_drms": 2.0609835609793663,
          "mean_reference_ca_lddt": 0.31748378909742475,
          "mean_pairwise_sample_ca_rmsd": 18.26001220525154
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.439022231847048,
          "mean_reference_ca_lddt": 0.24610561810993103,
          "mean_pairwise_sample_ca_rmsd": 19.409480008058672
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
          "raw_valid_fraction": 0.9609375,
          "motif_fraction_under_1A": 0.09375,
          "joint_fraction": 0.09375,
          "mean_motif_drms": 4.714055757503957,
          "mean_reference_ca_lddt": 0.3719010269768248,
          "mean_pairwise_sample_ca_rmsd": 23.70328013042378
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.525115266442299,
          "mean_reference_ca_lddt": 0.27250029285492233,
          "mean_pairwise_sample_ca_rmsd": 24.96626141810007
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.09375,
        "ci95": [
          0.03125,
          0.1640625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
