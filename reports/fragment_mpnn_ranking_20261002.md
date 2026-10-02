# ProteinMPNN score diagnostic

Exploratory development diagnostic; three model arms share four families. Sequence ranking costs8MPNN designs but only1refold; oracle requires8refolds and is not deployable. Joint final counts can include sequence-driven motif repair when raw motif failed, so are NOT retention successes. Strict gates unchanged.

```json
{
  "status": "complete",
  "interpretation": "Exploratory development diagnostic; three model arms share four families. Sequence ranking costs8MPNN designs but only1refold; oracle requires8refolds and is not deployable. Joint final counts can include sequence-driven motif repair when raw motif failed, so are NOT retention successes. Strict gates unchanged.",
  "sources": [
    {
      "run": "runs/trained_fragment_designability_49900262",
      "report_sha256": "2a05e3de463d0e45ef4b34ef09ab14a0fdb9c5a9a3a82f00ade28f395a7386c2",
      "manifest_sha256": "ee62552a34ac6853441cc895603040c0d7838465dfb5d42ed4edf373d3aefabc"
    },
    {
      "run": "runs/trained_fragment_designability_49903663",
      "report_sha256": "a58a31b84b14537891fe9c1d8c51fcf84be33e40f6046aa6e16ec48b7ddd6562",
      "manifest_sha256": "ff44bc9cc0ca03f66f165ae5bbdf6b64842e4db851e4ea3a7c1afa2a5c663ed4"
    },
    {
      "run": "runs/trained_fragment_designability_49919660",
      "report_sha256": "cde836dd8ac3481f6ce4e03b43dc6ae3dd2108f693dfb84cd2dc40af1cc1e3b0",
      "manifest_sha256": "b9316197878af9fc669b2168f17ef937f7677976597a62d8182833dcc4d5eecb"
    }
  ],
  "summaries": [
    {
      "arm": "adapter_only",
      "backbones": 8,
      "mean_within_backbone_spearman": 0.0029761904761904795,
      "any_valid_global": 2,
      "any_joint_final": 0,
      "strict": 0,
      "selectors": {
        "first": {
          "mean_sc_tm": 0.34603875,
          "valid_global": 2,
          "joint_final": 0
        },
        "mpnn_global": {
          "mean_sc_tm": 0.34098125,
          "valid_global": 1,
          "joint_final": 0
        },
        "mpnn_designed": {
          "mean_sc_tm": 0.35135875,
          "valid_global": 1,
          "joint_final": 0
        },
        "oracle_global": {
          "mean_sc_tm": 0.3862,
          "valid_global": 2,
          "joint_final": 0
        }
      }
    },
    {
      "arm": "full",
      "backbones": 8,
      "mean_within_backbone_spearman": 0.09821428571428574,
      "any_valid_global": 4,
      "any_joint_final": 2,
      "strict": 0,
      "selectors": {
        "first": {
          "mean_sc_tm": 0.426165,
          "valid_global": 2,
          "joint_final": 2
        },
        "mpnn_global": {
          "mean_sc_tm": 0.40830124999999995,
          "valid_global": 1,
          "joint_final": 0
        },
        "mpnn_designed": {
          "mean_sc_tm": 0.431745,
          "valid_global": 1,
          "joint_final": 0
        },
        "oracle_global": {
          "mean_sc_tm": 0.4818175,
          "valid_global": 4,
          "joint_final": 2
        }
      }
    },
    {
      "arm": "geometry",
      "backbones": 8,
      "mean_within_backbone_spearman": -0.07142857142857145,
      "any_valid_global": 2,
      "any_joint_final": 1,
      "strict": 0,
      "selectors": {
        "first": {
          "mean_sc_tm": 0.33493249999999997,
          "valid_global": 1,
          "joint_final": 0
        },
        "mpnn_global": {
          "mean_sc_tm": 0.31310875000000005,
          "valid_global": 1,
          "joint_final": 1
        },
        "mpnn_designed": {
          "mean_sc_tm": 0.33454875,
          "valid_global": 1,
          "joint_final": 0
        },
        "oracle_global": {
          "mean_sc_tm": 0.44096124999999997,
          "valid_global": 2,
          "joint_final": 0
        }
      }
    },
    {
      "arm": "all_arms",
      "backbones": 24,
      "mean_within_backbone_spearman": 0.009920634920634922,
      "any_valid_global": 8,
      "any_joint_final": 3,
      "strict": 0,
      "selectors": {
        "first": {
          "mean_sc_tm": 0.3690454166666666,
          "valid_global": 5,
          "joint_final": 2
        },
        "mpnn_global": {
          "mean_sc_tm": 0.3541304166666667,
          "valid_global": 3,
          "joint_final": 1
        },
        "mpnn_designed": {
          "mean_sc_tm": 0.37255083333333333,
          "valid_global": 3,
          "joint_final": 0
        },
        "oracle_global": {
          "mean_sc_tm": 0.43632625,
          "valid_global": 8,
          "joint_final": 2
        }
      }
    }
  ],
  "comparisons": [
    {
      "metric": "sc_tm",
      "global_score_minus_first": {
        "mean": -0.014915000000000008,
        "ci95": [
          -0.04635833333333335,
          0.016528333333333332
        ],
        "families": 4
      }
    },
    {
      "metric": "valid_global",
      "global_score_minus_first": {
        "mean": -0.08333333333333333,
        "ci95": [
          -0.16666666666666666,
          0.0
        ],
        "families": 4
      }
    },
    {
      "metric": "joint_final",
      "global_score_minus_first": {
        "mean": -0.041666666666666664,
        "ci95": [
          -0.125,
          0.0
        ],
        "families": 4
      }
    }
  ]
}
```
