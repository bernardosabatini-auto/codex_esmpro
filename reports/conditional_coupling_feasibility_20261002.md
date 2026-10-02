# Within-sequence matching feasibility

No GPU inference or training. All32training proteins,32groups of8balanced teacher draws each. Exact assignment changes only the noise–target pairing, retaining every drawn target exactly once.

{
  "groups": 1024,
  "draws": 8192,
  "mean_independent_cost": 2.00009619515739,
  "mean_optimal_cost": 1.9973022419044923,
  "mean_cost_reduction": 0.0027939532528975775,
  "mean_target_variance": 0.00718283517978513,
  "fraction_assignments_changed": 0.832275390625,
  "elapsed_seconds": 1.3490556090837345
}

Lower pairwise transport cost is not evidence of improved modeling or structural diversity. A matched training experiment would require the same group composition and all RNG draws, plus fresh-noise evaluation. No test data used.
