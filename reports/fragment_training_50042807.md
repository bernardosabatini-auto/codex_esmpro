# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "83ef2500730cc7c4a11a8b5a30e0d8457e9100dc4212ff5039db53cfb5c94cfa",
  "updates": 2000,
  "total_training_updates": 6000,
  "audited_predictions": 1152,
  "training_seconds": 1171.4302769270726,
  "evaluation_seconds": 334.95943982806057,
  "elapsed_seconds": 1544.7326810602099,
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
          "motif_fraction_under_1A": 0.140625,
          "joint_fraction": 0.140625,
          "mean_motif_drms": 1.9615341303870082,
          "mean_reference_ca_lddt": 0.3249707329536904,
          "mean_pairwise_sample_ca_rmsd": 17.673919193629057
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.43722403049469,
          "mean_reference_ca_lddt": 0.25328429697381,
          "mean_pairwise_sample_ca_rmsd": 19.193106693109833
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.140625,
        "ci95": [
          0.03125,
          0.265625
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
          "motif_fraction_under_1A": 0.171875,
          "joint_fraction": 0.171875,
          "mean_motif_drms": 4.376887863967568,
          "mean_reference_ca_lddt": 0.3807063259797444,
          "mean_pairwise_sample_ca_rmsd": 22.972764274676006
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.371543567627668,
          "mean_reference_ca_lddt": 0.2742889593712508,
          "mean_pairwise_sample_ca_rmsd": 24.123840117842935
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.171875,
        "ci95": [
          0.09375,
          0.2578125
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
          "mean_motif_drms": 1.9401460448279977,
          "mean_reference_ca_lddt": 0.33191288464883373,
          "mean_pairwise_sample_ca_rmsd": 17.13988498617576
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.334418796002865,
          "mean_reference_ca_lddt": 0.2539156452818846,
          "mean_pairwise_sample_ca_rmsd": 18.669670610660738
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1875,
        "ci95": [
          0.046875,
          0.34375
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
          "motif_fraction_under_1A": 0.1953125,
          "joint_fraction": 0.1953125,
          "mean_motif_drms": 4.29310186393559,
          "mean_reference_ca_lddt": 0.386655244005203,
          "mean_pairwise_sample_ca_rmsd": 22.47529685081227
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.449640274047852,
          "mean_reference_ca_lddt": 0.27277242538441854,
          "mean_pairwise_sample_ca_rmsd": 24.52893470903276
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1953125,
        "ci95": [
          0.109375,
          0.296875
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
      "step": 2000,
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
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
