# Isolated-fragment failure localization

CPU development diagnostic; no new sampling, selection for promotion or thresholds.
[
  {
    "mode": "full_context",
    "n": 64,
    "peptide_failed": 2,
    "clash_failed": 13,
    "gap_failed": 12,
    "gap_region_counts": {
      "motif_internal": 0,
      "boundary": 27,
      "scaffold_internal": 10
    },
    "clash_region_counts": {
      "motif_internal": 0,
      "motif_scaffold": 27,
      "scaffold_internal": 1
    },
    "region_outlier_rates": {
      "motif_internal": 0.003787878787878788,
      "boundary": 0.2734375,
      "scaffold_internal": 0.008565989847715736
    }
  },
  {
    "mode": "isolated",
    "n": 64,
    "peptide_failed": 4,
    "clash_failed": 24,
    "gap_failed": 27,
    "gap_region_counts": {
      "motif_internal": 13,
      "boundary": 39,
      "scaffold_internal": 16
    },
    "clash_region_counts": {
      "motif_internal": 0,
      "motif_scaffold": 57,
      "scaffold_internal": 0
    },
    "region_outlier_rates": {
      "motif_internal": 0.007954545454545454,
      "boundary": 0.359375,
      "scaffold_internal": 0.009200507614213198
    }
  }
]

Motif retention among the existing33random draws per fixed case (exploratory selection using supplied fragment only):
[
  {
    "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
    "slot": 0,
    "best_index": 22,
    "best_motif_drms": 2.3625848293304443,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
    "slot": 1,
    "best_index": 7,
    "best_motif_drms": 3.632218599319458,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "nmr__1DGN_1__96f3965253f9",
    "slot": 0,
    "best_index": 12,
    "best_motif_drms": 2.1253812313079834,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "nmr__1DGN_1__96f3965253f9",
    "slot": 1,
    "best_index": 19,
    "best_motif_drms": 3.9156880378723145,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "crypticpocket__P62593__3e6631cbb03c",
    "slot": 0,
    "best_index": 9,
    "best_motif_drms": 5.628062725067139,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "crypticpocket__P62593__3e6631cbb03c",
    "slot": 1,
    "best_index": 3,
    "best_motif_drms": 6.21470832824707,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "crypticpocket__P61586__aeabcc544d6c",
    "slot": 0,
    "best_index": 10,
    "best_motif_drms": 6.231423854827881,
    "count_under1A": 0,
    "draws": 33
  },
  {
    "target_id": "crypticpocket__P61586__aeabcc544d6c",
    "slot": 1,
    "best_index": 27,
    "best_motif_drms": 5.596295356750488,
    "count_under1A": 0,
    "draws": 33
  }
]
