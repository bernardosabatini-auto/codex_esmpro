# Fixed fragment guidance screen

Sixteen development families, four matched noises, CFG1 versus CFG2. Every output retained and audited. Scaffold diversity is measured after proper motif alignment; qualified-pair counts expose sparse success. Raw geometry and motif retention do not demonstrate designability.

```json
{
  "status": "complete",
  "manifest_sha256": "06d0ae70b3d94c035531cf5509ffbaa02b58febaa811a65556e964eff3434ba4",
  "predictions_sha256": "22dba2bf3d11417b469861635f5f69c074570427e7a5b4eb9d4010ccd3c643ac",
  "designability_followup_qualified": false,
  "fixed_assay_raw_success": 0,
  "summaries": [
    {
      "guidance": 1,
      "samples": 64,
      "valid": 64,
      "strict_raw": 0,
      "all_diversity_pairs": 96,
      "mean_scaffold_rmsd": 26.482008983121602,
      "qualified_diversity_pairs": 0,
      "qualified_mean_scaffold_rmsd": null
    },
    {
      "guidance": 2,
      "samples": 64,
      "valid": 63,
      "strict_raw": 2,
      "all_diversity_pairs": 96,
      "mean_scaffold_rmsd": 24.600022790881695,
      "qualified_diversity_pairs": 1,
      "qualified_mean_scaffold_rmsd": 12.785037421565521
    }
  ],
  "comparisons": [
    {
      "metric": "strict_raw",
      "guidance1": 0.0,
      "guidance2": 0.03125,
      "guidance2_minus_1": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.09375
        ],
        "families": 16
      }
    },
    {
      "metric": "coarse_valid",
      "guidance1": 1.0,
      "guidance2": 0.984375,
      "guidance2_minus_1": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      }
    },
    {
      "metric": "motif_drms",
      "guidance1": 1.9615345923230052,
      "guidance2": 1.5119619397446513,
      "guidance2_minus_1": {
        "mean": -0.4495726525783539,
        "ci95": [
          -0.7188995434902609,
          -0.22831944252830003
        ],
        "families": 16
      }
    },
    {
      "metric": "motif_ca_rmsd",
      "guidance1": 3.3832445861056253,
      "guidance2": 2.429319200433813,
      "guidance2_minus_1": {
        "mean": -0.9539253856718121,
        "ci95": [
          -1.702085902618796,
          -0.39381264410403427
        ],
        "families": 16
      }
    }
  ],
  "timing": [
    {
      "guidance": 1,
      "seconds": 11.21572761470452,
      "peak_reserved_GiB": 5.11328125
    },
    {
      "guidance": 2,
      "seconds": 21.369787980802357,
      "peak_reserved_GiB": 5.11328125
    }
  ],
  "elapsed_seconds": 77.9240287123248
}
```
