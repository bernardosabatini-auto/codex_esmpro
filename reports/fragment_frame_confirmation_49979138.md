# Fresh-noise target frame confirmation

```json
{
  "status": "complete",
  "manifest_sha256": "a1308e8a157d6186da13687bc22c9817a6c819aa93f74057535330adb7ac4361",
  "data_manifest_sha256": "8dd76aeedcf0f1e5fb3b444ec3566267a6317b4f2282b89ff40e8868ab277340",
  "fragments_sha256": "083757e49fc1499f25991c6f43c992d700376a1e9d37a1fcebd6a2328b9c4694",
  "paired_cases": 864,
  "training_families": 32,
  "summary": {
    "original": {
      "coarse_valid_fraction": 0.9953703703703703,
      "valid_motif_under_one_A_fraction": 0.9837962962962963,
      "valid_global_under_half_A_fraction": 0.8993055555555556
    },
    "anchored": {
      "coarse_valid_fraction": 0.9965277777777778,
      "valid_motif_under_one_A_fraction": 0.9884259259259259,
      "valid_global_under_half_A_fraction": 0.9131944444444444
    }
  },
  "anchored_minus_original": {
    "global_rmsd": {
      "mean": -0.009520478178394513,
      "ci95": [
        -0.021116040872094972,
        0.0014124209047116768
      ],
      "families": 32
    },
    "motif_rmsd": {
      "mean": -0.005851925786053378,
      "ci95": [
        -0.02012328457854753,
        0.0060351606463108325
      ],
      "families": 32
    }
  },
  "relative_label_gate_passed": true,
  "original_absolute_gate_passed": false,
  "interpretation": "Revised baseline-relative label-quality screen; three fresh decoder seeds on the same32trainingfamilies, not independent structural validation. Original failed absolute gate preserved. No model performance claim.",
  "elapsed_seconds": 102.77130907122046
}
```
