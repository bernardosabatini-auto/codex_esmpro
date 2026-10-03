# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "6265e63ff6e12fc240454da44dcf8f647c78483e58dad1ea529303d771dcd32a",
  "updates": 40,
  "total_training_updates": 4040,
  "audited_predictions": 64,
  "training_seconds": 23.14415489602834,
  "evaluation_seconds": 25.51958421105519,
  "elapsed_seconds": 87.91402708785608,
  "max_reserved_GiB": 29.16796875,
  "profile_qualified": true,
  "capacity_gate_passed": false,
  "summaries": [
    {
      "step": 0,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.25,
          "joint_fraction": 0.25,
          "mean_motif_drms": 1.4519175365567207,
          "mean_reference_ca_lddt": 0.3473262663101059,
          "mean_pairwise_sample_ca_rmsd": 16.590313743825398
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.876971423625946,
          "mean_reference_ca_lddt": 0.2594110430950685,
          "mean_pairwise_sample_ca_rmsd": 18.880318449807152
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.25,
        "ci95": [
          0.0625,
          0.4375
        ],
        "families": 4
      }
    },
    {
      "step": 40,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.1875,
          "joint_fraction": 0.1875,
          "mean_motif_drms": 1.4802725091576576,
          "mean_reference_ca_lddt": 0.35049190895600935,
          "mean_pairwise_sample_ca_rmsd": 16.307214617677975
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.842053562402725,
          "mean_reference_ca_lddt": 0.2597591123266284,
          "mean_pairwise_sample_ca_rmsd": 18.87415441280301
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.1875,
        "ci95": [
          0.0625,
          0.25
        ],
        "families": 4
      }
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4
}
```
