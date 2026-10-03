# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "3b97f0093129b4b4e600d884cca85b1ffa84255bd3bb1830cbdfee8c696a8170",
  "updates": 40,
  "total_training_updates": 4040,
  "audited_predictions": 64,
  "training_seconds": 23.35169782815501,
  "evaluation_seconds": 25.511841213796288,
  "elapsed_seconds": 91.77463223645464,
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
          "motif_fraction_under_1A": 0.75,
          "joint_fraction": 0.75,
          "mean_motif_drms": 0.9635435529053211,
          "mean_reference_ca_lddt": 0.3486375158371007,
          "mean_pairwise_sample_ca_rmsd": 17.41676305055432
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.23604303598404,
          "mean_reference_ca_lddt": 0.25110562409002857,
          "mean_pairwise_sample_ca_rmsd": 19.070571784929207
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
    }
  ],
  "initial_controls": 32,
  "sampling_controls": 4,
  "augmentation_contrast_audit": {
    "status": "complete",
    "matched_primary_steps": 40,
    "identical_initial_samples": 32,
    "augmented_conditional_examples": 274,
    "all_null_targets_unchanged": true,
    "baseline_manifest_sha256": "ebaeb3cc7cd1035b2b1aa57f13f31a2ef290e238f0349fcb230bf57ab450b14c",
    "candidate_manifest_sha256": "3b97f0093129b4b4e600d884cca85b1ffa84255bd3bb1830cbdfee8c696a8170"
  }
}
```
