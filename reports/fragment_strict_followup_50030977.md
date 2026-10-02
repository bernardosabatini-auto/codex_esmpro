# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [],
  "manifest_sha256": "c9482478def709c54703d08901f1bc1bea47e30d5de32bf4225923da6533a333",
  "refolded_sha256": "261be878435f95db3a0ef9901de0f4787cea93136e0eafe46c5f46dedaf1d029",
  "completed_refolds": 32,
  "newly_executed_refolds": 16,
  "reused_refolds": 16,
  "native_strict_controls": {
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1CB9_1__7ca9cd6d9b60": true
  },
  "summaries": [
    {
      "arm": "plain128",
      "screened": 64,
      "families": 16,
      "raw_matches": 0,
      "known_raw_failures": 64,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    },
    {
      "arm": "weighted128",
      "screened": 64,
      "families": 16,
      "raw_matches": 2,
      "known_raw_failures": 62,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 67.39207638194785
}
```
