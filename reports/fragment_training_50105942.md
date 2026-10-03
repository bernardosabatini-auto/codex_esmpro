# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "ebaeb3cc7cd1035b2b1aa57f13f31a2ef290e238f0349fcb230bf57ab450b14c",
  "updates": 40,
  "total_training_updates": 4040,
  "audited_predictions": 64,
  "training_seconds": 23.271999962627888,
  "evaluation_seconds": 25.536264969967306,
  "elapsed_seconds": 93.66744718933478,
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
          "motif_fraction_under_1A": 0.75,
          "joint_fraction": 0.75,
          "mean_motif_drms": 0.9645146764814854,
          "mean_reference_ca_lddt": 0.3486939662806573,
          "mean_pairwise_sample_ca_rmsd": 17.448206762585556
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.185223251581192,
          "mean_reference_ca_lddt": 0.2526714895555533,
          "mean_pairwise_sample_ca_rmsd": 19.04065827607548
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.75,
        "ci95": [
          0.5625,
          0.9375
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
          "motif_fraction_under_1A": 0.6875,
          "joint_fraction": 0.6875,
          "mean_motif_drms": 0.9797025769948959,
          "mean_reference_ca_lddt": 0.34944642352892646,
          "mean_pairwise_sample_ca_rmsd": 17.45416882163734
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.223198741674423,
          "mean_reference_ca_lddt": 0.2510560730556195,
          "mean_pairwise_sample_ca_rmsd": 19.074279037208974
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.6875,
        "ci95": [
          0.5625,
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
