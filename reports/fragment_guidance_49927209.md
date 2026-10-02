# Fixed fragment guidance screen

Sixteen development families, four matched noises, CFG1 versus CFG2. Every output retained and audited. Scaffold diversity is measured after proper motif alignment; qualified-pair counts expose sparse success. Raw geometry and motif retention do not demonstrate designability.

```json
{
  "status": "complete",
  "manifest_sha256": "b2484153198af59a74f563348beafd5ccf7148a60095696e3d3c92a6f14cc2d2",
  "predictions_sha256": "d3e988339763cf6276f0eff1b5fe8b05fcfbe4bdc40e5f049bace37b59f3769a",
  "designability_followup_qualified": false,
  "fixed_assay_raw_success": 0,
  "summaries": [
    {
      "guidance": 1,
      "samples": 64,
      "valid": 64,
      "strict_raw": 0,
      "all_diversity_pairs": 96,
      "mean_scaffold_rmsd": 31.73928561269575,
      "qualified_diversity_pairs": 0,
      "qualified_mean_scaffold_rmsd": null
    },
    {
      "guidance": 2,
      "samples": 64,
      "valid": 64,
      "strict_raw": 0,
      "all_diversity_pairs": 96,
      "mean_scaffold_rmsd": 29.319753492692538,
      "qualified_diversity_pairs": 0,
      "qualified_mean_scaffold_rmsd": null
    }
  ],
  "comparisons": [
    {
      "metric": "strict_raw",
      "guidance1": 0.0,
      "guidance2": 0.0,
      "guidance2_minus_1": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "metric": "coarse_valid",
      "guidance1": 1.0,
      "guidance2": 1.0,
      "guidance2_minus_1": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "metric": "motif_drms",
      "guidance1": 3.194934405386448,
      "guidance2": 2.329112292267382,
      "guidance2_minus_1": {
        "mean": -0.8658221131190658,
        "ci95": [
          -1.2332311953650787,
          -0.5309055879944936
        ],
        "families": 16
      }
    },
    {
      "metric": "motif_ca_rmsd",
      "guidance1": 5.373419814391983,
      "guidance2": 4.268228023213281,
      "guidance2_minus_1": {
        "mean": -1.1051917911787026,
        "ci95": [
          -1.7300441735541052,
          -0.5626291195173235
        ],
        "families": 16
      }
    }
  ],
  "timing": [
    {
      "guidance": 1,
      "seconds": 11.242313501425087,
      "peak_reserved_GiB": 5.11328125
    },
    {
      "guidance": 2,
      "seconds": 21.36641490459442,
      "peak_reserved_GiB": 5.11328125
    }
  ],
  "elapsed_seconds": 74.88811753410846
}
```
