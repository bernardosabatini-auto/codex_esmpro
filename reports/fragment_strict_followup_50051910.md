# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [],
  "manifest_sha256": "f4ee9d25a3d6761dbec0a5166d397cd885ac2c86833e688e2d5a334040dbef98",
  "refolded_sha256": "b1b0b9910d517d654a009753b509fea5bbbd79b875b32a5d4b10c8b0823d464f",
  "completed_refolds": 64,
  "newly_executed_refolds": 48,
  "reused_refolds": 16,
  "native_strict_controls": {
    "crypticpocket__P12758__35b945080f12": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1CB9_1__7ca9cd6d9b60": true
  },
  "summaries": [
    {
      "arm": "plain_extended",
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
      "arm": "weighted_extended",
      "screened": 64,
      "families": 16,
      "raw_matches": 3,
      "known_raw_failures": 61,
      "strict_same_refold_successes": 1,
      "strict_fraction": 0.015625,
      "successful_families": 1,
      "successes_with_passing_native_control": 1,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 116.42411377467215
}
```
