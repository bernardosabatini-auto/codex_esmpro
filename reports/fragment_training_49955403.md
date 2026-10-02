# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "5f2468b9e9f19a34cdaa009438ad15f84a68c25bdf4cb41cdc3d819dedfbf87e",
  "updates": 40,
  "total_training_updates": 2040,
  "audited_predictions": 64,
  "training_seconds": 206.96872325381264,
  "evaluation_seconds": 24.43380679562688,
  "elapsed_seconds": 284.09293696377426,
  "max_reserved_GiB": 29.984375,
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
          "mean_motif_drms": 2.4418826699256897,
          "mean_reference_ca_lddt": 0.3216377609091197,
          "mean_pairwise_sample_ca_rmsd": 15.40747894891775
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.791629821062088,
          "mean_reference_ca_lddt": 0.2553733216037719,
          "mean_pairwise_sample_ca_rmsd": 17.43145924323922
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
  "sampling_controls": 4
}
```
