# Refolding every strict raw match

```json
{
  "status": "complete",
  "manifest_sha256": "6e9abd752c24f54505912775da24d98ef0d871e674b4e32858ac0825753a03e6",
  "refolded_sha256": "2e2d2b8dce68992cc772c4e4528305bc17f0fdf8346f249e44bdcff688df3770",
  "completed_refolds": 16,
  "native_strict_controls": {
    "nmr__1BFY_1__b91a89d44751": true
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
      "arm": "plain512",
      "screened": 64,
      "families": 16,
      "raw_matches": 1,
      "known_raw_failures": 63,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 51.41922407923266
}
```
