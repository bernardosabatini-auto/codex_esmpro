# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "040a10b4efde683529f6c1af13da3e4b9776530c037d155b6afffffcd7a1508a",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1165.0494167315774,
  "evaluation_seconds": 332.5630569634959,
  "elapsed_seconds": 1540.1152007975616,
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
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.453125,
          "joint_fraction": 0.4375,
          "mean_motif_drms": 1.2821911191567779,
          "mean_reference_ca_lddt": 0.34713000220268764,
          "mean_pairwise_sample_ca_rmsd": 16.65628578168792
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.20970344170928,
          "mean_reference_ca_lddt": 0.25165196272535073,
          "mean_pairwise_sample_ca_rmsd": 18.102588212241244
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4375,
        "ci95": [
          0.25,
          0.625
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
          "raw_valid_fraction": 0.9609375,
          "motif_fraction_under_1A": 0.4609375,
          "joint_fraction": 0.4375,
          "mean_motif_drms": 2.681670928490348,
          "mean_reference_ca_lddt": 0.3993688983076077,
          "mean_pairwise_sample_ca_rmsd": 24.735486748972203
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.332143159583211,
          "mean_reference_ca_lddt": 0.2691645773868296,
          "mean_pairwise_sample_ca_rmsd": 25.64241734736921
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4375,
        "ci95": [
          0.2890625,
          0.5859375
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
          "motif_fraction_under_1A": 0.484375,
          "joint_fraction": 0.46875,
          "mean_motif_drms": 1.2237974689342082,
          "mean_reference_ca_lddt": 0.3468464751404077,
          "mean_pairwise_sample_ca_rmsd": 16.512657191864818
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.615333762019873,
          "mean_reference_ca_lddt": 0.2519456750426999,
          "mean_pairwise_sample_ca_rmsd": 18.446867355628786
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.46875,
        "ci95": [
          0.28125,
          0.6566406249999943
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
          "motif_fraction_under_1A": 0.4140625,
          "joint_fraction": 0.4140625,
          "mean_motif_drms": 2.7154975871089846,
          "mean_reference_ca_lddt": 0.4006819614220159,
          "mean_pairwise_sample_ca_rmsd": 24.955199165037776
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.883021336048841,
          "mean_reference_ca_lddt": 0.27144547246490425,
          "mean_pairwise_sample_ca_rmsd": 27.304459483087342
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4140625,
        "ci95": [
          0.2578125,
          0.5703125
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
          "motif_fraction_under_1A": 0.390625,
          "joint_fraction": 0.359375,
          "mean_motif_drms": 1.2350511755794287,
          "mean_reference_ca_lddt": 0.3445028526259509,
          "mean_pairwise_sample_ca_rmsd": 16.451567593699053
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.267753951251507,
          "mean_reference_ca_lddt": 0.25901994385160343,
          "mean_pairwise_sample_ca_rmsd": 17.56393814988398
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.359375,
        "ci95": [
          0.1875,
          0.546875
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
          "motif_fraction_under_1A": 0.421875,
          "joint_fraction": 0.4140625,
          "mean_motif_drms": 2.567820293828845,
          "mean_reference_ca_lddt": 0.4088059947764734,
          "mean_pairwise_sample_ca_rmsd": 24.733740752661333
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9765625,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.583846248686314,
          "mean_reference_ca_lddt": 0.2664660035015731,
          "mean_pairwise_sample_ca_rmsd": 25.58344857996575
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4140625,
        "ci95": [
          0.265625,
          0.5625
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
