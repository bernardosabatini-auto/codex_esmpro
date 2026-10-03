# Full-backbone sequence-design feasibility

```json
{
  "status": "complete",
  "manifest_sha256": "594af46806345c493d2f7b8f522ae6ed73e2a117cf02de5dab0cbeb8c6918efa",
  "refolded_sha256": "a93d5e4d58556e20a1bc35f0ed692706d32076cf7ccb4a658599fcd42aa31f38",
  "new_refolds": 32,
  "reused_baseline_refolds": 32,
  "summaries": [
    {
      "mode": "ca_only",
      "backbones": 2,
      "sequences_per_backbone": 8,
      "strict_successes": 0,
      "valid_global": 2,
      "native_controls_passed": true
    },
    {
      "mode": "full_backbone",
      "backbones": 2,
      "sequences_per_backbone": 8,
      "strict_successes": 0,
      "valid_global": 1,
      "native_controls_passed": true
    }
  ],
  "elapsed_seconds": 59.45131938578561,
  "interpretation": "Selected-case sequence-design feasibility, not generalization or a generator improvement. Keep current training comparisons on the unchanged CA-only assay. If full-backbone design yields strict success with native controls, evaluate it on a fixed panel; otherwise close this design-mode pilot. No model-weight, temperature, backbone-noise or seed sweep."
}
```
