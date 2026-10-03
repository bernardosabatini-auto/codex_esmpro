# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "bf34b9cb9e2f056c9dd0caa625d9dce7116181f56f778e9500ffc568f84c1fee",
  "updates": 40,
  "total_training_updates": 6040,
  "audited_predictions": 64,
  "training_seconds": 18.74282706528902,
  "evaluation_seconds": 28.26528201624751,
  "elapsed_seconds": 89.13041962869465,
  "max_reserved_GiB": 20.689453125,
  "profile_qualified": true,
  "capacity_gate_passed": false,
  "summaries": [
    {
      "step": 0,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 16,
          "raw_valid_fraction": 0.9375,
          "motif_fraction_under_1A": 0.9375,
          "joint_fraction": 0.875,
          "mean_motif_drms": 0.7364642396569252,
          "mean_reference_ca_lddt": 0.36840743003958204,
          "mean_pairwise_sample_ca_rmsd": 15.446626571505877
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.599452629685402,
          "mean_reference_ca_lddt": 0.24623500447893,
          "mean_pairwise_sample_ca_rmsd": 17.491160548800558
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.875,
        "ci95": [
          0.75,
          1.0
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
          "motif_fraction_under_1A": 0.9375,
          "joint_fraction": 0.875,
          "mean_motif_drms": 0.7281282935291529,
          "mean_reference_ca_lddt": 0.36800941358253536,
          "mean_pairwise_sample_ca_rmsd": 15.522336459192106
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.599452629685402,
          "mean_reference_ca_lddt": 0.24623500447893,
          "mean_pairwise_sample_ca_rmsd": 17.491160548800558
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.875,
        "ci95": [
          0.75,
          1.0
        ],
        "families": 4
      }
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4
}
```
