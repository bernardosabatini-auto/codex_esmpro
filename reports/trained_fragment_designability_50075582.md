# Trained fragment designability

All36backbones and288designed-sequence refolds retained. Strict success requires valid raw geometry and motif fit, then one SAME refold with scTM>.5, valid geometry, motif dRMS<=1A and proper-rotation motifCA RMSD<=1A. Motif residues fixed; no scaffold sequence supplied. Four-family development feasibility only.

```json
{
  "status": "complete",
  "positive_controls_passed": true,
  "interpretation_qualified": true,
  "arm": "geometry_time_shift",
  "manifest_sha256": "c5697b23ece592d5aa4997feaa2b4aa312853772681d7f5ca1fd0a4428a8902c",
  "refolded_sha256": "acc43b717bf56178824c41696bccb20b4db00cf2ad21e456ccdb5d09160bb5c1",
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
      "valid_designable": {
        "count": 6,
        "fraction": 0.75,
        "family_interval": {
          "mean": 0.75,
          "ci95": [
            0.5,
            1.0
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
      "mean_pairwise_tm": 0.34862
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
      "mean_pairwise_tm": 0.198965
    },
    {
      "mode": "trained_null",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    }
  ],
  "mpnn_seconds": 52.078469974920154,
  "elapsed_seconds": 359.5259926156141,
  "peak_reserved_GiB": 26.005859375
}
```
