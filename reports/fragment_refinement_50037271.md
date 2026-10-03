# Refold and recondition feasibility

```json
{
  "status": "complete",
  "manifest_sha256": "5ffbb09c0d840183304ffbbe54be7f757d09cd3031d66ba010db011b7c21c26c",
  "summaries": [
    {
      "arm": "feedback",
      "paths": 2,
      "designs_per_path_including_initial": 24,
      "round2_strict": 0,
      "round3_strict": 0,
      "cumulative_strict": 0,
      "valid_global_backbones": 4
    },
    {
      "arm": "random",
      "paths": 2,
      "designs_per_path_including_initial": 24,
      "round2_strict": 0,
      "round3_strict": 0,
      "cumulative_strict": 0,
      "valid_global_backbones": 4
    }
  ],
  "native_controls_passed": true,
  "new_refolds": 96,
  "reused_initial_generated_refolds": 16,
  "elapsed_seconds": 265.2999670188874,
  "interpretation": "Two post-selected development cases with raw motif retention but refold drift; repair feasibility only, no generalization claim. No development refold becomes a training label. No locked tests. Continue to a fixed-panel comparison only if feedback yields strict success with passing native controls."
}
```
