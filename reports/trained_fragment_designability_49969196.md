# Trained fragment designability

All36backbones and288designed-sequence refolds retained. Strict success requires valid raw geometry and motif fit, then one SAME refold with scTM>.5, valid geometry, motif dRMS<=1A and proper-rotation motifCA RMSD<=1A. Motif residues fixed; no scaffold sequence supplied. Four-family development feasibility only.

```json
{
  "status": "complete",
  "positive_controls_passed": true,
  "interpretation_qualified": true,
  "arm": "geometry_full_expanded_step500",
  "manifest_sha256": "b2a8deadfe1c1f89892e75bd9b5201499a5afaabb8738e4e75a3a23ba18f9fa7",
  "refolded_sha256": "1f874d71c734459aa66a15957c06db9d5a41113e10e900fb00db8a68d9c751d5",
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
        "count": 3,
        "fraction": 0.375,
        "family_interval": {
          "mean": 0.375,
          "ci95": [
            0.125,
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
      "mean_pairwise_tm": 0.2787
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
      "mean_pairwise_tm": 0.195455
    },
    {
      "mode": "trained_null",
      "scope": "strict_joint_success",
      "pairs": 0,
      "mean_pairwise_tm": null
    }
  ],
  "mpnn_seconds": 53.797618789132684,
  "elapsed_seconds": 356.4826562516391,
  "peak_reserved_GiB": 26.005859375
}
```
