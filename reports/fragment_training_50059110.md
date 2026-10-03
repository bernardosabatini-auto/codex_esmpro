# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "920983578a4ac64cd3befc249f009191f968c33e6939555aa26d2b8725fc1d07",
  "updates": 40,
  "total_training_updates": 2040,
  "audited_predictions": 64,
  "training_seconds": 22.751830224879086,
  "evaluation_seconds": 29.46596649615094,
  "elapsed_seconds": 99.41733465297148,
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
          "raw_valid_fraction": 0.9375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 2.2756994366645813,
          "mean_reference_ca_lddt": 0.32492788445854004,
          "mean_pairwise_sample_ca_rmsd": 14.955936516159957
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.710761278867722,
          "mean_reference_ca_lddt": 0.25623972087194014,
          "mean_pairwise_sample_ca_rmsd": 17.663182995219167
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
