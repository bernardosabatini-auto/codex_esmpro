# Fresh-noise strict refolding and diversity

```json
{
  "status": "complete",
  "manifest_sha256": "5f21d7b2767d48371a3f57ac84b444250381beeaa050e69d050838ca53d5f7c4",
  "refolded_sha256": "fed380b9c5d20139b003face3bd931c0a900c198e6d3161b68ab480f83f6d514",
  "completed_refolds": 192,
  "unique_generated_samples": 152,
  "overlapping_focus_samples_per_arm": 4,
  "native_strict_controls": {
    "crypticpocket__P61586__aeabcc544d6c": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "nmr__1B4Q_1__3f71b01b7768": true,
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1BM5_1__17d05a87e530": true,
    "nmr__1CB9_1__7ca9cd6d9b60": true
  },
  "summaries": [
    {
      "arm": "reference6000",
      "view": "whole_panel",
      "screened": 64,
      "families": 16,
      "raw_matches": 4,
      "strict_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "reference6000",
      "view": "focus",
      "screened": 16,
      "families": 1,
      "raw_matches": 3,
      "strict_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "augmented8000",
      "view": "whole_panel",
      "screened": 64,
      "families": 16,
      "raw_matches": 8,
      "strict_successes": 3,
      "strict_fraction": 0.046875,
      "successful_families": 2,
      "successes_with_passing_native_control": 3,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "augmented8000",
      "view": "focus",
      "screened": 16,
      "families": 1,
      "raw_matches": 6,
      "strict_successes": 3,
      "strict_fraction": 0.1875,
      "successful_families": 1,
      "successes_with_passing_native_control": 3,
      "global_designability_of_raw_failures": "not measured"
    }
  ],
  "successful_refold_diversity": [
    {
      "arm": "reference6000",
      "successful_backbones": 0,
      "chosen_first_qualifying_refolds": [],
      "pairs": [],
      "mean_global_tm": null,
      "mean_motif_aligned_scaffold_rmsd": null
    },
    {
      "arm": "augmented8000",
      "successful_backbones": 3,
      "chosen_first_qualifying_refolds": [
        {
          "generation_slot": 2,
          "name": "validation_010",
          "sequence_index": 0
        },
        {
          "generation_slot": 9,
          "name": "validation_012",
          "sequence_index": 4
        },
        {
          "generation_slot": 11,
          "name": "validation_013",
          "sequence_index": 4
        }
      ],
      "pairs": [
        {
          "left": 2,
          "right": 9,
          "global_tm": 0.33809,
          "motif_aligned_scaffold_rmsd": 51.54350706687282
        },
        {
          "left": 2,
          "right": 11,
          "global_tm": 0.33121,
          "motif_aligned_scaffold_rmsd": 45.042461670827926
        },
        {
          "left": 9,
          "right": 11,
          "global_tm": 0.37254,
          "motif_aligned_scaffold_rmsd": 42.91774535671828
        }
      ],
      "mean_global_tm": 0.34728000000000003,
      "mean_motif_aligned_scaffold_rmsd": 46.50123803147301
    }
  ],
  "elapsed_seconds": 299.51356322830543,
  "interpretation": "Reused development families and one post-selected case, with prospective fresh noise. This tests stochastic repeatability and conditional diversity, not independent-protein validation. No development refolds become training labels; locked tests remain unscored. Keep the failed fixed-panel and other recipe results intact. This compares deployment candidates at different training exposures, not a target-only attribution; the matched 8000-update target-only comparison remains separate. Preserve original seed2026100270 validation. No significance or broad generalization claim from a handful of successes. The64and16sample views overlap; never add their success counts or denominators."
}
```
