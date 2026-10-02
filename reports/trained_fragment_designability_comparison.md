# Paired trained-fragment designability

All fixed-budget outputs retained.20shared control backbones produce the same160designed sequences and numerically equivalent refolds under the established teacher repeatability tolerances; all control decisions agree in both assays. Generated backbones hold supplied motif residues fixed; these rates cannot be compared directly with unconstrained sequence-design rates. Four-family feasibility, not a population estimate or experimental validation.

```json
{
  "status": "complete",
  "identical_control_backbones": 20,
  "identical_control_sequences": 160,
  "numerically_equivalent_control_refolds": 160,
  "max_control_ca_rmsd": 0.009670542677062926,
  "min_control_ca_lddt": 1.0,
  "bitwise_identical_refolds": 0,
  "same_control_decisions": true,
  "comparisons": [
    {
      "metric": "strict_joint_success",
      "adapter_only": 0.0,
      "full": 0.0,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    },
    {
      "metric": "valid_designable",
      "adapter_only": 0.25,
      "full": 0.5,
      "full_minus_adapter": {
        "mean": 0.25,
        "ci95": [
          -0.25,
          0.5
        ],
        "families": 4
      }
    },
    {
      "metric": "raw_gate_passed",
      "adapter_only": 0.0,
      "full": 0.0,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 4
      }
    }
  ],
  "source_report_hashes": [
    "2a05e3de463d0e45ef4b34ef09ab14a0fdb9c5a9a3a82f00ade28f395a7386c2",
    "a58a31b84b14537891fe9c1d8c51fcf84be33e40f6046aa6e16ec48b7ddd6562"
  ]
}
```
