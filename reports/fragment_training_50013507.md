# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "6759e4dbf17484e994a749e6de4ad9525db2e66693a8bd1175c807c2054c3306",
  "updates": 40,
  "total_training_updates": 40,
  "audited_predictions": 64,
  "training_seconds": 23.188125878106803,
  "evaluation_seconds": 25.9966500448063,
  "elapsed_seconds": 93.41681555239484,
  "max_reserved_GiB": 29.169921875,
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
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.783812329173088,
          "mean_reference_ca_lddt": 0.24878182444017521,
          "mean_pairwise_sample_ca_rmsd": 19.07884450222559
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.783812329173088,
          "mean_reference_ca_lddt": 0.24878182444017521,
          "mean_pairwise_sample_ca_rmsd": 19.07884450222559
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
    },
    {
      "step": 40,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.77522200345993,
          "mean_reference_ca_lddt": 0.24861810055578096,
          "mean_pairwise_sample_ca_rmsd": 19.071868113442733
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.785257458686829,
          "mean_reference_ca_lddt": 0.24846887109858018,
          "mean_pairwise_sample_ca_rmsd": 19.082751025068582
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
