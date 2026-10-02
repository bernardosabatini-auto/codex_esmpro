# Trained fragment designability

All36backbones and288designed-sequence refolds retained. Strict success requires valid raw geometry and motif fit, then one SAME refold with scTM>.5, valid geometry, motif dRMS<=1A and proper-rotation motifCA RMSD<=1A. Motif residues fixed; no scaffold sequence supplied. Four-family development feasibility only.

```json
{
  "status": "complete",
  "positive_controls_passed": true,
  "interpretation_qualified": true,
  "arm": "geometry_full_expanded512",
  "manifest_sha256": "6b8068636828bdc37caf2f3715aaf4bb36b02dc3302dc69d11db6774d49f0a00",
  "refolded_sha256": "09b054690cb64b55839ced496ca29779d279811e478fe2865b06107f8b8c655d",
  "completed_refolds": 288,
  "summaries": [
    {
      "mode": "conditioned",
      "backbones": 8,
      "strict_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "legacy_drms_joint_success": {
        "count": 1,
        "fraction": 0.125,
        "family_interval": {
          "mean": 0.125,
          "ci95": [
            0.0,
            0.375
          ],
          "families": 4
        }
      },
      "valid_designable": {
        "count": 4,
        "fraction": 0.5,
        "family_interval": {
          "mean": 0.5,
          "ci95": [
            0.125,
            0.875
          ],
          "families": 4
        }
      },
      "raw_gate_passed": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      }
    },
    {
      "mode": "isolated_clamp",
      "backbones": 8,
      "strict_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "legacy_drms_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "valid_designable": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "raw_gate_passed": {
        "count": 2,
        "fraction": 0.25,
        "family_interval": {
          "mean": 0.25,
          "ci95": [
            0.0,
            0.75
          ],
          "families": 4
        }
      }
    },
    {
      "mode": "original_null",
      "backbones": 8,
      "strict_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "legacy_drms_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "valid_designable": {
        "count": 2,
        "fraction": 0.25,
        "family_interval": {
          "mean": 0.25,
          "ci95": [
            0.0,
            0.5
          ],
          "families": 4
        }
      },
      "raw_gate_passed": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      }
    },
    {
      "mode": "real",
      "backbones": 4,
      "strict_joint_success": {
        "count": 3,
        "fraction": 0.75,
        "family_interval": {
          "mean": 0.75,
          "ci95": [
            0.25,
            1.0
          ],
          "families": 4
        }
      },
      "legacy_drms_joint_success": {
        "count": 4,
        "fraction": 1.0,
        "family_interval": {
          "mean": 1.0,
          "ci95": [
            1.0,
            1.0
          ],
          "families": 4
        }
      },
      "valid_designable": {
        "count": 4,
        "fraction": 1.0,
        "family_interval": {
          "mean": 1.0,
          "ci95": [
            1.0,
            1.0
          ],
          "families": 4
        }
      },
      "raw_gate_passed": {
        "count": 4,
        "fraction": 1.0,
        "family_interval": {
          "mean": 1.0,
          "ci95": [
            1.0,
            1.0
          ],
          "families": 4
        }
      }
    },
    {
      "mode": "trained_null",
      "backbones": 8,
      "strict_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "legacy_drms_joint_success": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      },
      "valid_designable": {
        "count": 1,
        "fraction": 0.125,
        "family_interval": {
          "mean": 0.125,
          "ci95": [
            0.0,
            0.375
          ],
          "families": 4
        }
      },
      "raw_gate_passed": {
        "count": 0,
        "fraction": 0.0,
        "family_interval": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 4
        }
      }
    }
  ],
  "comparisons": [
    {
      "baseline": "trained_null",
      "conditioned_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    },
    {
      "baseline": "isolated_clamp",
      "conditioned_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    },
    {
      "baseline": "original_null",
      "conditioned_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    }
  ],
  "diversity": [
    {
      "mode": "conditioned",
      "scope": "all",
      "pairs": 4,
      "mean_pairwise_tm": 0.344735
    },
    {
      "mode": "conditioned",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    },
    {
      "mode": "isolated_clamp",
      "scope": "all",
      "pairs": 4,
      "mean_pairwise_tm": 0.36274249999999997
    },
    {
      "mode": "isolated_clamp",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    },
    {
      "mode": "original_null",
      "scope": "all",
      "pairs": 4,
      "mean_pairwise_tm": 0.17237
    },
    {
      "mode": "original_null",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    },
    {
      "mode": "trained_null",
      "scope": "all",
      "pairs": 4,
      "mean_pairwise_tm": 0.2029175
    },
    {
      "mode": "trained_null",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    }
  ],
  "mpnn_seconds": 53.70602666400373,
  "elapsed_seconds": 371.480665308889,
  "peak_reserved_GiB": 26.005859375
}
```
