# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "12621f2e6f8e2ab3109eea7bed1e244a0b5175c32b77a78d5f2c10d0bbe06911",
  "updates": 40,
  "total_training_updates": 4040,
  "audited_predictions": 64,
  "training_seconds": 23.23094721324742,
  "evaluation_seconds": 25.445301015861332,
  "elapsed_seconds": 93.34404441015795,
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
          "motif_fraction_under_1A": 0.5625,
          "joint_fraction": 0.5625,
          "mean_motif_drms": 1.0526773910969496,
          "mean_reference_ca_lddt": 0.3573744471380661,
          "mean_pairwise_sample_ca_rmsd": 17.182169818011843
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.508394166827202,
          "mean_reference_ca_lddt": 0.25330624729431594,
          "mean_pairwise_sample_ca_rmsd": 18.382924548513014
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.5625,
        "ci95": [
          0.25,
          0.875
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
          "motif_fraction_under_1A": 0.5625,
          "joint_fraction": 0.5625,
          "mean_motif_drms": 1.0138579662889242,
          "mean_reference_ca_lddt": 0.3565581054647722,
          "mean_pairwise_sample_ca_rmsd": 16.725656691028153
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.49698555469513,
          "mean_reference_ca_lddt": 0.2535054501556636,
          "mean_pairwise_sample_ca_rmsd": 18.371177023487675
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.5625,
        "ci95": [
          0.375,
          0.75
        ],
        "families": 4
      }
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4
}
```
