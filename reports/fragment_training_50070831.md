# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "09d6392e659cbc885f7cfec0f227c03a8d10493f826962bd96012b243681ede6",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1158.3183956979774,
  "evaluation_seconds": 330.2296978463419,
  "elapsed_seconds": 1526.2189639769495,
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
          "mean_motif_drms": 2.3128094347193837,
          "mean_reference_ca_lddt": 0.3120432670029244,
          "mean_pairwise_sample_ca_rmsd": 18.778747341712844
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.59871556982398,
          "mean_reference_ca_lddt": 0.2460205827375974,
          "mean_pairwise_sample_ca_rmsd": 20.162515753104092
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.046875,
        "ci95": [
          0.0,
          0.125
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
          "motif_fraction_under_1A": 0.0546875,
          "joint_fraction": 0.0546875,
          "mean_motif_drms": 4.892855676356703,
          "mean_reference_ca_lddt": 0.3723222318513587,
          "mean_pairwise_sample_ca_rmsd": 23.88443021054709
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.752290982753038,
          "mean_reference_ca_lddt": 0.2746950285533043,
          "mean_pairwise_sample_ca_rmsd": 26.163270559599113
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0546875,
        "ci95": [
          0.0078125,
          0.1171875
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
          "motif_fraction_under_1A": 0.140625,
          "joint_fraction": 0.140625,
          "mean_motif_drms": 1.9319651266559958,
          "mean_reference_ca_lddt": 0.3317820026616035,
          "mean_pairwise_sample_ca_rmsd": 17.211084467007925
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.433619402348995,
          "mean_reference_ca_lddt": 0.2509646498574888,
          "mean_pairwise_sample_ca_rmsd": 19.565047231488844
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.140625,
        "ci95": [
          0.046875,
          0.2503906249999943
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
          "motif_fraction_under_1A": 0.1875,
          "joint_fraction": 0.1875,
          "mean_motif_drms": 3.418674349784851,
          "mean_reference_ca_lddt": 0.3932577201666413,
          "mean_pairwise_sample_ca_rmsd": 24.294028486311056
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.566558444872499,
          "mean_reference_ca_lddt": 0.27980151093129557,
          "mean_pairwise_sample_ca_rmsd": 25.80826180006968
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1875,
        "ci95": [
          0.09375,
          0.296875
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4,
  "time_contrast_audit": {
    "status": "complete",
    "matched_primary_steps": 2000,
    "transformed_time_steps": 2000,
    "identical_initial_samples": 384,
    "baseline_manifest_sha256": "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285",
    "candidate_manifest_sha256": "09d6392e659cbc885f7cfec0f227c03a8d10493f826962bd96012b243681ede6",
    "null_times_unchanged": true
  }
}
```
