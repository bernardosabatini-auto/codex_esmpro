# Training-only preference and coupling audit

```json
{
  "status": "complete",
  "training_only": true,
  "original_feedback_training_gate": false,
  "original_qualified_backbones": 0,
  "discovery_eligible": 1,
  "split_confirmed": 0,
  "max_within_condition_permutation_cost_change": 0.0,
  "identity_flow_counterexample": {
    "teacher_endpoint_reconstruction_mse": 0.0,
    "condition_agreement_with_reused_noise": 1.0,
    "condition_agreement_with_fresh_noise": 0.4994
  },
  "scope": "Retrospective exploration, not prospective label qualification or a training result. Global/scaffold agreement remains hard and same-refold; motif error is graded only for ranking. One endpoint per condition makes within-condition reassignment degenerate. Directly fitting one noise per structure changes the conditional noise distribution; preserving teacher paths does not by itself teach independent-noise conditioning. No inversion GPU experiment launched. This does not rule out a conditional transport method that preserves the required marginals.",
  "decision": "Insufficient confirmed protein coverage for preference training. Preserve the failed binary-label collection. Any new collection must prospectively bind its source selection, design split, minimum coverage and unchanged strict endpoint before generating labels."
}
```
