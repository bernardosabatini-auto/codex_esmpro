# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "881fcba40df141c783233f8cb681a9ef7a32496a8f3419b93d98e3bf97c5c76d",
  "updates": 40,
  "total_training_updates": 6040,
  "audited_predictions": 64,
  "training_seconds": 18.6950398767367,
  "evaluation_seconds": 25.34367630118504,
  "elapsed_seconds": 136.4323513098061,
  "max_reserved_GiB": 20.59375,
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
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.875,
          "joint_fraction": 0.875,
          "mean_motif_drms": 0.771675243973732,
          "mean_reference_ca_lddt": 0.3639393600796976,
          "mean_pairwise_sample_ca_rmsd": 16.048807233591
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
