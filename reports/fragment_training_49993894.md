# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "67dd88ad9ff70b2e76fa77cb5c8c89fe9a4d51a852cc168ada9ca5a60eff12d9",
  "updates": 40,
  "total_training_updates": 40,
  "audited_predictions": 64,
  "training_seconds": 23.24867228511721,
  "evaluation_seconds": 28.753540200181305,
  "elapsed_seconds": 104.20763424504548,
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
          "mean_motif_drms": 7.7765971422195435,
          "mean_reference_ca_lddt": 0.24873190817240304,
          "mean_pairwise_sample_ca_rmsd": 19.071201531588994
        },
        "null": {
          "samples": 16,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.785388484597206,
          "mean_reference_ca_lddt": 0.24844758916071014,
          "mean_pairwise_sample_ca_rmsd": 19.082752760519888
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
