# Paired trained-fragment designability

All fixed-budget outputs retained.20shared control backbones produce the same160designed sequences and numerically equivalent refolds under the established teacher repeatability tolerances; all control decisions agree in both assays. Generated backbones hold supplied motif residues fixed; these rates cannot be compared directly with unconstrained sequence-design rates. Four-family feasibility, not a population estimate or experimental validation.

```json
{
  "status": "complete",
  "matched_fragment_inputs_across_corpora": false,
  "baseline_arm": "geometry_full_expanded",
  "candidate_arm": "geometry_latent_weight3",
  "identical_control_backbones": 20,
  "identical_control_sequences": 160,
  "numerically_equivalent_control_refolds": 160,
  "max_control_ca_rmsd": 0.006610816026487433,
  "min_control_ca_lddt": 1.0,
  "bitwise_identical_refolds": 0,
  "same_control_decisions": true,
  "comparisons": [
    {
      "metric": "strict_joint_success",
      "baseline": 0.0,
      "candidate": 0.0,
      "candidate_minus_baseline": {
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
      "baseline": 0.5,
      "candidate": 0.625,
      "candidate_minus_baseline": {
        "mean": 0.125,
        "ci95": [
          -0.375,
          0.75
        ],
        "families": 4
      }
    },
    {
      "metric": "raw_gate_passed",
      "baseline": 0.0,
      "candidate": 0.125,
      "candidate_minus_baseline": {
        "mean": 0.125,
        "ci95": [
          0.0,
          0.375
        ],
        "families": 4
      }
    }
  ],
  "source_report_hashes": [
    "6ed6ad03905e890118aa5c05a1b085e4e22b88a53f013c600dde427bf8b58d9d",
    "8f517f44fae01231064582f1485acc2bc9c75946e4ffc0e7f3495dca95f32c55"
  ]
}
```
