# Motif steering through initial noise

Status: complete.

All8fixed cases retained. Each starts from its closest motif among33archived random candidates. Original50-step flow,FP32AE3,frozen weights. Motif distance-matrix RMS<=1A. Only fragment coordinates enter the objective; no geometry filtering.

| Method | Mean motif dRMS A | Motif success | Coarse valid | Joint motif/geometry | Seconds |
|---|---:|---:|---:|---:|---:|
| initial | 4.463 | 0.000 | 1.000 | 0.000 | 41.27 |
| guided | 4.380 | 0.000 | 1.000 | 0.000 | 342.30 |

Guided peak reserved memory 6.09GiB. Numerical checks and all saved proposals/accepted states audited.

Times charge both methods the actual archived33draw generation cost; guided also includes optimization,transfers and controller decisions. Excludes loading,numerical controls,disk I/O and CPU candidate-selection time, recorded separately in config. Candidates reused rather than regenerated for benchmarking; no new end-to-end speed claim. Fixed radius does not establish an unchanged prior or designability. Strict fixed-motif ProteinMPNN/refolding and positive controls remain required. Only supplied fragment coordinates; no locked tests.

Across the two fixed seeds per family (four pairs per method), mean pairwise CA-lDDT: {'initial': 0.3305748562678309, 'guided': 0.341995299727884, 'random': 0.3305748562678309}. This describes all outputs, not designable diversity.
