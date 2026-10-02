# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "c51d7da4bb8b86ad6691706ba56f5b14599c0a3db1ffaaf28e6d1768d0b00fd8",
  "updates": 500,
  "total_training_updates": 2500,
  "audited_predictions": 768,
  "training_seconds": 290.42546148831025,
  "evaluation_seconds": 222.6325777824968,
  "elapsed_seconds": 551.4515913599171,
  "max_reserved_GiB": 29.16796875,
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.21875,
          "joint_fraction": 0.21875,
          "mean_motif_drms": 1.6888577714562416,
          "mean_reference_ca_lddt": 0.32593804921380914,
          "mean_pairwise_sample_ca_rmsd": 17.280086558702443
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.28720024228096,
          "mean_reference_ca_lddt": 0.24669047640594483,
          "mean_pairwise_sample_ca_rmsd": 18.97770490008423
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.21875,
        "ci95": [
          0.078125,
          0.390625
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
          "raw_valid_fraction": 0.890625,
          "motif_fraction_under_1A": 0.2109375,
          "joint_fraction": 0.203125,
          "mean_motif_drms": 2.90487808350008,
          "mean_reference_ca_lddt": 0.3907572190268925,
          "mean_pairwise_sample_ca_rmsd": 23.407366604512585
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0078125,
          "joint_fraction": 0.0078125,
          "mean_motif_drms": 12.744944325182587,
          "mean_reference_ca_lddt": 0.28210275213839964,
          "mean_pairwise_sample_ca_rmsd": 24.924511944462473
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1953125,
        "ci95": [
          0.1015625,
          0.2890625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
