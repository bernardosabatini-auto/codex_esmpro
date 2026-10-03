# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "1d7f19277f9bb37a387e1989593a7d343d7c3d0e8e6070c6e04da87bcb58f54c",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1169.3090628688224,
  "evaluation_seconds": 331.45467243762687,
  "elapsed_seconds": 1551.590591715183,
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
          "motif_fraction_under_1A": 0.125,
          "joint_fraction": 0.125,
          "mean_motif_drms": 1.82133833412081,
          "mean_reference_ca_lddt": 0.3334256810337195,
          "mean_pairwise_sample_ca_rmsd": 16.846114376676656
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.387101288884878,
          "mean_reference_ca_lddt": 0.25846662864490944,
          "mean_pairwise_sample_ca_rmsd": 18.376874150197338
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.125,
        "ci95": [
          0.03125,
          0.234375
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
          "motif_fraction_under_1A": 0.25,
          "joint_fraction": 0.25,
          "mean_motif_drms": 3.8875809942837805,
          "mean_reference_ca_lddt": 0.4023393430641802,
          "mean_pairwise_sample_ca_rmsd": 22.993912150742883
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.413149286061525,
          "mean_reference_ca_lddt": 0.27011180679935454,
          "mean_pairwise_sample_ca_rmsd": 23.918853636667333
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.25,
        "ci95": [
          0.1484375,
          0.3671875
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
          "motif_fraction_under_1A": 0.1875,
          "joint_fraction": 0.1875,
          "mean_motif_drms": 1.8196819238364697,
          "mean_reference_ca_lddt": 0.3374924477092098,
          "mean_pairwise_sample_ca_rmsd": 16.68091023607409
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.364235669374466,
          "mean_reference_ca_lddt": 0.2628013281304898,
          "mean_pairwise_sample_ca_rmsd": 18.12958562013329
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1875,
        "ci95": [
          0.078125,
          0.296875
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.21875,
          "joint_fraction": 0.21875,
          "mean_motif_drms": 3.714339249301702,
          "mean_reference_ca_lddt": 0.41019859178574325,
          "mean_pairwise_sample_ca_rmsd": 22.98065223410116
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.306853460147977,
          "mean_reference_ca_lddt": 0.27975418406061564,
          "mean_pairwise_sample_ca_rmsd": 23.68881857907983
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.21875,
        "ci95": [
          0.125,
          0.3203125
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
          "motif_fraction_under_1A": 0.15625,
          "joint_fraction": 0.15625,
          "mean_motif_drms": 1.820573785342276,
          "mean_reference_ca_lddt": 0.3349396449039086,
          "mean_pairwise_sample_ca_rmsd": 15.688059803407597
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.59517315775156,
          "mean_reference_ca_lddt": 0.26536982535537923,
          "mean_pairwise_sample_ca_rmsd": 17.22692203718399
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.15625,
        "ci95": [
          0.0625,
          0.25
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
          "motif_fraction_under_1A": 0.3203125,
          "joint_fraction": 0.3125,
          "mean_motif_drms": 3.5147373450454324,
          "mean_reference_ca_lddt": 0.43250476623912826,
          "mean_pairwise_sample_ca_rmsd": 22.737507488978352
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.308795912191272,
          "mean_reference_ca_lddt": 0.27823998775208886,
          "mean_pairwise_sample_ca_rmsd": 24.182088332008682
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3125,
        "ci95": [
          0.1796875,
          0.453125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
