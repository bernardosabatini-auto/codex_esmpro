# Retrospective native-anchor feasibility

```json
{
  "status": "complete",
  "comparison_sha256": "c3b5fbd78072e7bf528fd04ccc94931aea722e33e4617865d532476b0c439b41",
  "original_generated_preference_gate": {
    "qualified": false,
    "checks": {
      "coverage": false,
      "confirmation_rate": true,
      "length_buckets": true,
      "long_proteins": false,
      "native_calibration": true
    },
    "eligible": 8,
    "confirmed": 6,
    "confirmation_rate": 0.75
  },
  "proteins": 32,
  "native_preferred_discovery": 25,
  "native_preferred_confirmed": 25,
  "scope": "Posthoc hypothesis audit only. Original generated-candidate gate is unchanged. Native coordinates have measured refolds, but their encoded latent plus stochastic decoder must be qualified before transferring positive labels. These pairs are not authorized training labels.",
  "next": "If native anchors supply stable contrasts, prospectively test decoded-native positive anchors on a separate training cohort. Compare positive-only replay with reference-anchored contrastive learning only after that independent label qualification."
}
```
