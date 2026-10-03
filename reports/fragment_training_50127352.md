# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "361ebc5c40259dfffe3cdc182a632f9bc62ef6f5f83eab3051a60df262e2d365",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1169.369939613156,
  "evaluation_seconds": 332.9563704901375,
  "elapsed_seconds": 1611.1804251261055,
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
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.515625,
          "joint_fraction": 0.5,
          "mean_motif_drms": 1.1752624842338264,
          "mean_reference_ca_lddt": 0.32489390143722896,
          "mean_pairwise_sample_ca_rmsd": 18.665886188139854
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.312541369348764,
          "mean_reference_ca_lddt": 0.24088226822949962,
          "mean_pairwise_sample_ca_rmsd": 19.839562723106745
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.5,
        "ci95": [
          0.3125,
          0.6875
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
          "motif_fraction_under_1A": 0.4375,
          "joint_fraction": 0.4296875,
          "mean_motif_drms": 2.8104493925347924,
          "mean_reference_ca_lddt": 0.38675441781167497,
          "mean_pairwise_sample_ca_rmsd": 24.468324613016513
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.27522481046617,
          "mean_reference_ca_lddt": 0.2671841657324873,
          "mean_pairwise_sample_ca_rmsd": 25.12464756996704
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4296875,
        "ci95": [
          0.2890625,
          0.578125
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
          "motif_fraction_under_1A": 0.65625,
          "joint_fraction": 0.640625,
          "mean_motif_drms": 1.0084725641645491,
          "mean_reference_ca_lddt": 0.3311014704143329,
          "mean_pairwise_sample_ca_rmsd": 18.454868269286894
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.356179881840944,
          "mean_reference_ca_lddt": 0.2434611198057639,
          "mean_pairwise_sample_ca_rmsd": 19.883694760519184
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.640625,
        "ci95": [
          0.453125,
          0.8125
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
          "motif_fraction_under_1A": 0.5234375,
          "joint_fraction": 0.515625,
          "mean_motif_drms": 2.2751759845996276,
          "mean_reference_ca_lddt": 0.3954613521164393,
          "mean_pairwise_sample_ca_rmsd": 24.472187784342946
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.259840477257967,
          "mean_reference_ca_lddt": 0.2665860721002865,
          "mean_pairwise_sample_ca_rmsd": 25.117428206877076
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.515625,
        "ci95": [
          0.359375,
          0.671875
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4
}
```
