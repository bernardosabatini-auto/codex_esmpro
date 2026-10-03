# Fresh-noise strict refolding and diversity

```json
{
  "status": "complete",
  "manifest_sha256": "bfce35490f094f1188b238ec34756af8c458829540b79f0cd6e243211443b2d8",
  "refolded_sha256": "92e6643c02d6fb4f71f1d9bbe2b52cffa9039119340faa9c962ea95dfbaf1c78",
  "completed_refolds": 88,
  "unique_generated_samples": 152,
  "overlapping_focus_samples_per_arm": 4,
  "native_strict_controls": {
    "crypticpocket__P61586__aeabcc544d6c": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "nmr__1BFY_1__b91a89d44751": true
  },
  "summaries": [
    {
      "arm": "plain",
      "view": "whole_panel",
      "screened": 64,
      "families": 16,
      "raw_matches": 2,
      "strict_successes": 1,
      "strict_fraction": 0.015625,
      "successful_families": 1,
      "successes_with_passing_native_control": 1,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "plain",
      "view": "focus",
      "screened": 16,
      "families": 1,
      "raw_matches": 0,
      "strict_successes": 0,
      "strict_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "weighted",
      "view": "whole_panel",
      "screened": 64,
      "families": 16,
      "raw_matches": 5,
      "strict_successes": 2,
      "strict_fraction": 0.03125,
      "successful_families": 2,
      "successes_with_passing_native_control": 2,
      "global_designability_of_raw_failures": "not measured"
    },
    {
      "arm": "weighted",
      "view": "focus",
      "screened": 16,
      "families": 1,
      "raw_matches": 2,
      "strict_successes": 2,
      "strict_fraction": 0.125,
      "successful_families": 1,
      "successes_with_passing_native_control": 2,
      "global_designability_of_raw_failures": "not measured"
    }
  ],
  "successful_refold_diversity": [
    {
      "arm": "plain",
      "successful_backbones": 0,
      "chosen_first_qualifying_refolds": [],
      "pairs": [],
      "mean_global_tm": null,
      "mean_motif_aligned_scaffold_rmsd": null
    },
    {
      "arm": "weighted",
      "successful_backbones": 2,
      "chosen_first_qualifying_refolds": [
        {
          "generation_slot": 1,
          "name": "validation_007",
          "sequence_index": 0
        },
        {
          "generation_slot": 7,
          "name": "validation_008",
          "sequence_index": 1
        }
      ],
      "pairs": [
        {
          "left": 1,
          "right": 7,
          "global_tm": 0.44269,
          "motif_aligned_scaffold_rmsd": 22.206678093492975
        }
      ],
      "mean_global_tm": 0.44269,
      "mean_motif_aligned_scaffold_rmsd": 22.206678093492975
    }
  ],
  "elapsed_seconds": 138.42562769679353,
  "interpretation": "Reused development families and one post-selected case, with prospective fresh noise. This tests stochastic repeatability and conditional diversity, not independent-protein validation. No development refolds become training labels; locked tests remain unscored. Keep the failed fixed-panel and other recipe results intact. The64and16sample views overlap; never add their success counts or denominators."
}
```
