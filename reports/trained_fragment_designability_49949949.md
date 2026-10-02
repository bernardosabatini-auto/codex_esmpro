# Trained fragment designability

All36backbones and288designed-sequence refolds retained. Strict success requires valid raw geometry and motif fit, then one SAME refold with scTM>.5, valid geometry, motif dRMS<=1A and proper-rotation motifCA RMSD<=1A. Motif residues fixed; no scaffold sequence supplied. Four-family development feasibility only.

```json
{
  "status": "complete",
  "positive_controls_passed": true,
  "interpretation_qualified": true,
  "arm": "geometry_full_continued",
  "manifest_sha256": "0034ef082cc21a03140b72c6f343e7f142d0b980e98279abfa2d3196085ce11c",
  "refolded_sha256": "a1fd11b429e697d466d3156ca5d353028023ed2d78a0e5612c83fce2a52bc130",
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
        "count": 3,
        "fraction": 0.375,
        "family_interval": {
          "mean": 0.375,
          "ci95": [
            0.0,
            0.75
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
      "mean_pairwise_tm": 0.25312
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
      "mean_pairwise_tm": 0.2894025
    },
    {
      "mode": "trained_null",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    }
  ],
  "mpnn_seconds": 55.03644337691367,
  "elapsed_seconds": 381.63898374093696,
  "peak_reserved_GiB": 26.005859375
}
```
