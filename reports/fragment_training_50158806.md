# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "ea46a7864938cef42d1204b584590effcc1f76d808e781df57041c4d68c574f5",
  "updates": 40,
  "total_training_updates": 6040,
  "audited_predictions": 64,
  "training_seconds": 18.48809384414926,
  "evaluation_seconds": 25.355006590951234,
  "elapsed_seconds": 147.05364242615178,
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
          "mean_motif_drms": 0.7593996375799179,
          "mean_reference_ca_lddt": 0.36192966484128974,
          "mean_pairwise_sample_ca_rmsd": 16.047253352800045
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
