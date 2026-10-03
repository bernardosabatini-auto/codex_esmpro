# Paired trained-fragment designability

All fixed-budget outputs retained.20shared control backbones produce the same160designed sequences and numerically equivalent refolds under the established teacher repeatability tolerances; all control decisions agree in both assays. Generated backbones hold supplied motif residues fixed; these rates cannot be compared directly with unconstrained sequence-design rates. Four-family feasibility, not a population estimate or experimental validation.

```json
{
  "status": "complete",
  "matched_fragment_inputs_across_corpora": false,
  "baseline_arm": "geometry_latent_weight3",
  "candidate_arm": "geometry_teacher_augmented",
  "identical_control_backbones": 20,
  "identical_control_sequences": 160,
  "numerically_equivalent_control_refolds": 160,
  "max_control_ca_rmsd": 0.0015123276266387493,
  "min_control_ca_lddt": 1.0,
  "bitwise_identical_refolds": 0,
  "same_control_decisions": true,
  "comparisons": [
    {
      "metric": "strict_joint_success",
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
    },
    {
      "metric": "valid_designable",
      "baseline": 0.75,
      "candidate": 0.75,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          -0.375,
          0.375
        ],
        "families": 4
      }
    },
    {
      "metric": "raw_gate_passed",
      "baseline": 0.125,
      "candidate": 0.125,
      "candidate_minus_baseline": {
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
    "6070a8577f5f6b5744eb37b7abe442dc0c9b11101357dd68463333aa197bdccd",
    "9df985ba771bb3022328b38421441fa26337eba905bd1f9816778d3abbfe5aa4"
  ]
}
```
