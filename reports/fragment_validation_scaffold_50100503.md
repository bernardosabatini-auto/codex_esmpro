# Fresh-noise same-refold scaffold agreement

Same valid refold must satisfy motif, global and scaffold agreement. Whole64and focus16overlap by4and must not be pooled. Diversity uses the first qualifying refold per distinct backbone; fewer than two backbones means undefined. Development feasibility only.

```json
{
  "summaries": [
    {
      "arm": "reference6000",
      "view": "whole_panel",
      "screened": 64,
      "raw_matches": 4,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "scaffold_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "reference6000",
      "view": "focus",
      "screened": 16,
      "raw_matches": 3,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "scaffold_fraction": 0.0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "augmented8000",
      "view": "whole_panel",
      "screened": 64,
      "raw_matches": 8,
      "primary_successes": 3,
      "scaffold_successes": 2,
      "scaffold_fraction": 0.03125,
      "successful_families": 2,
      "successes_with_passing_native_control": 2
    },
    {
      "arm": "augmented8000",
      "view": "focus",
      "screened": 16,
      "raw_matches": 6,
      "primary_successes": 3,
      "scaffold_successes": 2,
      "scaffold_fraction": 0.125,
      "successful_families": 1,
      "successes_with_passing_native_control": 2
    }
  ],
  "native_scaffold_controls": {
    "nmr__1BM5_1__17d05a87e530": true,
    "crypticpocket__P62593__3e6631cbb03c": true,
    "crypticpocket__P61586__aeabcc544d6c": true,
    "nmr__1B4Q_1__3f71b01b7768": true,
    "nmr__1BFY_1__b91a89d44751": true,
    "nmr__1CB9_1__7ca9cd6d9b60": true
  },
  "successful_scaffold_diversity": [
    {
      "arm": "augmented8000",
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "augmented8000",
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "successful_backbones": 2,
      "pairs": [
        {
          "left_slot": 2,
          "right_slot": 11,
          "left_sequence": 0,
          "right_sequence": 7,
          "global_tm": 0.34207,
          "scaffold_tm": 0.19992,
          "motif_aligned_scaffold_rmsd": 48.72956718721503
        }
      ]
    },
    {
      "arm": "native",
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "native",
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "native",
      "target_id": "nmr__1B4Q_1__3f71b01b7768",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "native",
      "target_id": "nmr__1BFY_1__b91a89d44751",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "native",
      "target_id": "nmr__1BM5_1__17d05a87e530",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "native",
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "successful_backbones": 1,
      "pairs": []
    }
  ]
}
```
