# Refolding every strict raw match

```json
{
  "status": "complete",
  "manifest_sha256": "24b98d286a3f52372ce5c853a425c65d9f3dd785f0bf373929b49b6e6caceb08",
  "refolded_sha256": "af7e82068089869356ce4ea747ecfa2af5445ca55f8dabb6da6e730ca5d0e90c",
  "completed_refolds": 32,
  "native_strict_controls": {
    "nmr__1BFY_1__b91a89d44751": true
  },
  "summaries": [
    {
      "arm": "plain32",
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
      "arm": "frame32",
      "screened": 64,
      "families": 16,
      "raw_matches": 1,
      "known_raw_failures": 63,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    },
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
      "arm": "guided128",
      "screened": 64,
      "families": 16,
      "raw_matches": 2,
      "known_raw_failures": 62,
      "strict_same_refold_successes": 1,
      "strict_fraction": 0.015625,
      "successful_families": 1,
      "successes_with_passing_native_control": 1,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 57.476401433348656
}
```
