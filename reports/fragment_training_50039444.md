# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "af3d067d0ba0a297024c6b91a589a6a777b1cb75923f12e8d7765c4560916b04",
  "updates": 40,
  "total_training_updates": 4040,
  "audited_predictions": 64,
  "training_seconds": 23.141481059603393,
  "evaluation_seconds": 24.481081455014646,
  "elapsed_seconds": 85.04184927791357,
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
          "mean_motif_drms": 1.480273000895977,
          "mean_reference_ca_lddt": 0.3504831993684954,
          "mean_pairwise_sample_ca_rmsd": 16.3072217766719
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.842053413391113,
          "mean_reference_ca_lddt": 0.25976121274335107,
          "mean_pairwise_sample_ca_rmsd": 18.874155586304646
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
