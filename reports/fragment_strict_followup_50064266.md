# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [],
  "manifest_sha256": "3d41fbc144ec0be887fc592d65aa2bc18a3212e9b072d4cd88fa14a275527b20",
  "refolded_sha256": "0a638c60a3c2971d8b2e9c22abf6e56ea6aee6ff87b5d9a1f26efd97bf74d968",
  "completed_refolds": 48,
  "newly_executed_refolds": 48,
  "reused_refolds": 0,
  "native_strict_controls": {
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1BM5_1__17d05a87e530": false,
    "nmr__1CB9_1__7ca9cd6d9b60": true
  },
  "summaries": [
    {
      "arm": "weighted512",
      "screened": 64,
      "families": 16,
      "raw_matches": 3,
      "known_raw_failures": 61,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 222.43476570630446
}
```
