# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "6024d3a6da1c50a72d2e940ddb7a69a6dccfc4c1266aac3390e2eb4682207cce",
  "updates": 40,
  "total_training_updates": 2040,
  "audited_predictions": 64,
  "training_seconds": 22.86293856985867,
  "evaluation_seconds": 24.388943552039564,
  "elapsed_seconds": 83.5470499121584,
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
          "motif_fraction_under_1A": 0.0625,
          "joint_fraction": 0.0625,
          "mean_motif_drms": 2.376926813274622,
          "mean_reference_ca_lddt": 0.3227245233033795,
          "mean_pairwise_sample_ca_rmsd": 15.22603014375363
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.778338506817818,
          "mean_reference_ca_lddt": 0.2590867235170624,
          "mean_pairwise_sample_ca_rmsd": 17.414503434052296
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0625,
        "ci95": [
          0.0,
          0.1875
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 2.474904887378216,
          "mean_reference_ca_lddt": 0.32402797720116794,
          "mean_pairwise_sample_ca_rmsd": 14.883849929370463
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.7222510278224945,
          "mean_reference_ca_lddt": 0.25756793746777584,
          "mean_pairwise_sample_ca_rmsd": 17.687931661341523
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4
}
```
