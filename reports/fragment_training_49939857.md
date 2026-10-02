# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
  "updates": 2000,
  "total_training_updates": 4000,
  "audited_predictions": 1152,
  "training_seconds": 1161.1588071156293,
  "evaluation_seconds": 330.97641987307,
  "elapsed_seconds": 1532.346947436221,
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 3.2622947208583355,
          "mean_reference_ca_lddt": 0.2993857629656352,
          "mean_pairwise_sample_ca_rmsd": 17.130189597688776
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 6.960234135389328,
          "mean_reference_ca_lddt": 0.2495926479278336,
          "mean_pairwise_sample_ca_rmsd": 17.57412355759191
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.1015625,
          "joint_fraction": 0.1015625,
          "mean_motif_drms": 6.111161314416677,
          "mean_reference_ca_lddt": 0.3983721961941148,
          "mean_pairwise_sample_ca_rmsd": 21.426771980171083
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.015625,
          "joint_fraction": 0.015625,
          "mean_motif_drms": 12.984564794227481,
          "mean_reference_ca_lddt": 0.29456137000115734,
          "mean_pairwise_sample_ca_rmsd": 23.974770903951633
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0859375,
        "ci95": [
          0.03125,
          0.15625
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
          "mean_motif_drms": 3.3866354674100876,
          "mean_reference_ca_lddt": 0.2970377822582705,
          "mean_pairwise_sample_ca_rmsd": 15.206477006173182
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 6.9396989196538925,
          "mean_reference_ca_lddt": 0.2575342439629291,
          "mean_pairwise_sample_ca_rmsd": 16.120217766686025
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.1953125,
          "joint_fraction": 0.1953125,
          "mean_motif_drms": 5.782612983719446,
          "mean_reference_ca_lddt": 0.4661980832629693,
          "mean_pairwise_sample_ca_rmsd": 19.545219342251766
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0703125,
          "joint_fraction": 0.0703125,
          "mean_motif_drms": 12.282881880179048,
          "mean_reference_ca_lddt": 0.3414992031179682,
          "mean_pairwise_sample_ca_rmsd": 21.266036643698065
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.125,
        "ci95": [
          0.0546875,
          0.203125
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
