# Refolding every strict raw match

```json
{
  "status": "complete",
  "successful_refold_diversity": [
    {
      "arm": "guidance1",
      "successful_backbones": 0,
      "chosen_first_qualifying_refolds": [],
      "pairs": [],
      "mean_global_tm": null,
      "mean_motif_aligned_scaffold_rmsd": null
    },
    {
      "arm": "guidance2",
      "successful_backbones": 0,
      "chosen_first_qualifying_refolds": [],
      "pairs": [],
      "mean_global_tm": null,
      "mean_motif_aligned_scaffold_rmsd": null
    }
  ],
  "manifest_sha256": "a797de01ed6288f75d0e8774b6155216e2f5c9cb2a316d2e71cf9c9f96f48431",
  "refolded_sha256": "724c3dde7c2b2d4a69315765be78a4c49d47072311967655745d1df6b3010c91",
  "completed_refolds": 40,
  "native_strict_controls": {
    "nmr__1BFY_1__b91a89d44751": true
  },
  "summaries": [
    {
      "arm": "guidance1",
      "screened": 16,
      "families": 1,
      "raw_matches": 3,
      "known_raw_failures": 13,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    },
    {
      "arm": "guidance2",
      "screened": 16,
      "families": 1,
      "raw_matches": 1,
      "known_raw_failures": 15,
      "strict_same_refold_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_unscreened_raw_failures": "not measured"
    }
  ],
  "interpretation": "Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.",
  "elapsed_seconds": 66.40805011289194
}
```
