# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "a2162308235fb76023dcc312b1cf2e8e7bf4e3877fd8c7ec5369cf532d6d2b4f",
  "updates": 40,
  "total_training_updates": 6040,
  "audited_predictions": 64,
  "training_seconds": 25.96786637371406,
  "evaluation_seconds": 27.936563039198518,
  "elapsed_seconds": 89.5390435080044,
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
          "mean_motif_drms": 1.1334885135293007,
          "mean_reference_ca_lddt": 0.3412982947873825,
          "mean_pairwise_sample_ca_rmsd": 16.219722172611025
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.062778562307358,
          "mean_reference_ca_lddt": 0.2596080056981227,
          "mean_pairwise_sample_ca_rmsd": 18.82551951379332
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
          "raw_valid_fraction": 0.9375,
          "motif_fraction_under_1A": 0.3125,
          "joint_fraction": 0.3125,
          "mean_motif_drms": 1.191214483231306,
          "mean_reference_ca_lddt": 0.3355999158750952,
          "mean_pairwise_sample_ca_rmsd": 16.302978767519875
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.09320867061615,
          "mean_reference_ca_lddt": 0.26022932938072707,
          "mean_pairwise_sample_ca_rmsd": 18.830324551378165
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3125,
        "ci95": [
          0.25,
          0.4375
        ],
        "families": 4
      }
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4
}
```
