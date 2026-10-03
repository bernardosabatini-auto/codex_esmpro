# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "b42d319435bd9f08e5f19b76e1fda18a97a31085d30fa85daa264a117dd2e291",
  "updates": 40,
  "total_training_updates": 2040,
  "audited_predictions": 64,
  "training_seconds": 22.694259520154446,
  "evaluation_seconds": 24.42606866080314,
  "elapsed_seconds": 104.19426358584315,
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
          "motif_fraction_under_1A": 0.0625,
          "joint_fraction": 0.0625,
          "mean_motif_drms": 2.2083146944642067,
          "mean_reference_ca_lddt": 0.32637705287844815,
          "mean_pairwise_sample_ca_rmsd": 15.054240170588379
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.7245825827121735,
          "mean_reference_ca_lddt": 0.2574520571393276,
          "mean_pairwise_sample_ca_rmsd": 17.696779073816003
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
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4,
  "time_contrast_audit": {
    "status": "complete",
    "matched_primary_steps": 40,
    "transformed_time_steps": 40,
    "identical_initial_samples": 32,
    "baseline_manifest_sha256": "6024d3a6da1c50a72d2e940ddb7a69a6dccfc4c1266aac3390e2eb4682207cce",
    "candidate_manifest_sha256": "b42d319435bd9f08e5f19b76e1fda18a97a31085d30fa85daa264a117dd2e291",
    "null_times_unchanged": true
  }
}
```
