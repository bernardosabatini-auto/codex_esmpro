# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [],
  "manifest_sha256": "a1534fcc6bd036bffbcdfac6c558a58c8cabcfba278b5a023f6cd1c7a7eb4098",
  "refolded_sha256": "e6b5f55fac2e48f2be9b09ae028f0fc749b740b3abd5af44c0ebfbcfc0275a21",
  "completed_refolds": 128,
  "newly_executed_refolds": 112,
  "reused_refolds": 16,
  "native_strict_controls": {
    "crypticpocket__P61586__aeabcc544d6c": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "domainmotion__P67701__3dbdd067cad2": false,
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1BM5_1__17d05a87e530": false
  },
  "summaries": [
    {
      "arm": "control512",
      "screened": 64,
      "families": 16,
      "raw_matches": 6,
      "known_raw_failures": 58,
      "strict_same_refold_successes": 1,
      "strict_fraction": 0.015625,
      "successful_families": 1,
      "successes_with_passing_native_control": 1,
      "global_designability_of_unscreened_raw_failures": "not measured"
    },
    {
      "arm": "augmented512",
      "screened": 64,
      "families": 16,
      "raw_matches": 5,
      "known_raw_failures": 59,
      "strict_same_refold_successes": 2,
      "strict_fraction": 0.03125,
      "successful_families": 2,
      "successes_with_passing_native_control": 2,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 150.46285812323913
}
```
