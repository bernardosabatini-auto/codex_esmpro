# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [],
  "manifest_sha256": "e13d71f8f7ab65de822eaebb10db6c87a36cf44f3250de1bbac1d1611629f607",
  "refolded_sha256": "e41b7dae29e5c2af24164a0508bcf6751a5a595a46a2798eb00fcacd0bf1f3a9",
  "completed_refolds": 56,
  "newly_executed_refolds": 56,
  "reused_refolds": 0,
  "native_strict_controls": {
    "crypticpocket__P12758__35b945080f12": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "nmr__1BM5_1__17d05a87e530": false
  },
  "summaries": [
    {
      "arm": "plain8000",
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
      "arm": "weighted8000",
      "screened": 64,
      "families": 16,
      "raw_matches": 4,
      "known_raw_failures": 60,
      "strict_same_refold_successes": 1,
      "strict_fraction": 0.015625,
      "successful_families": 1,
      "successes_with_passing_native_control": 1,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 136.41313981823623
}
```
