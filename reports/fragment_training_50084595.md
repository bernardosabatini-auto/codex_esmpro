# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "f6af47aac3298c7497993fa8a96d2a5c70c01b2e89da0f9d3ba1c7e83b8c6d4f",
  "updates": 40,
  "total_training_updates": 6040,
  "audited_predictions": 64,
  "training_seconds": 23.1639276240021,
  "evaluation_seconds": 25.444079667329788,
  "elapsed_seconds": 90.79067064682022,
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
          "motif_fraction_under_1A": 0.625,
          "joint_fraction": 0.625,
          "mean_motif_drms": 1.0429356023669243,
          "mean_reference_ca_lddt": 0.34454165671656645,
          "mean_pairwise_sample_ca_rmsd": 17.322438189178452
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.423684135079384,
          "mean_reference_ca_lddt": 0.25421294386690957,
          "mean_pairwise_sample_ca_rmsd": 18.33687571589336
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.625,
        "ci95": [
          0.25,
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.625,
          "joint_fraction": 0.625,
          "mean_motif_drms": 1.0577423349022865,
          "mean_reference_ca_lddt": 0.3469084273395752,
          "mean_pairwise_sample_ca_rmsd": 17.23206544860082
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 8.39666098356247,
          "mean_reference_ca_lddt": 0.24893301542436252,
          "mean_pairwise_sample_ca_rmsd": 18.491888377490536
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.625,
        "ci95": [
          0.25,
          1.0
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
    "augmented_conditional_examples": 275,
    "all_null_targets_unchanged": true,
    "baseline_manifest_sha256": "e561e74e7c7f9e0eb0bd8a5769d4464361519a73245b6bb539db5aa71b0a2d8a",
    "candidate_manifest_sha256": "f6af47aac3298c7497993fa8a96d2a5c70c01b2e89da0f9d3ba1c7e83b8c6d4f"
  }
}
```
