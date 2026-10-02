# Contact steering through initial noise

Status: complete.

All8fixed cases retained. Original50-step flow, FP32AE3, frozen weights. Contact target8A, success within1A. No geometry filtering in optimization or random selection.

| Method | Mean distance A | Contact success | Coarse valid | Joint contact/geometry | Seconds |
|---|---:|---:|---:|---:|---:|
| initial | 24.849 | 0.000 | 1.000 | 0.000 | 3.49 |
| guided | 9.167 | 0.625 | 1.000 | 0.625 | 168.06 |
| random | 9.494 | 0.375 | 1.000 | 0.375 | 41.27 |

Guided peak reserved memory 8.34GiB. Numerical checks and all saved proposals/accepted states audited.

Times include common initial generation, transfers and controller decisions; exclude model loading, numerical controls and measured disk-writing time. Random uses32additional draws; it is not assumed compute-matched to optimization. Fixed noise radius does not establish an unchanged prior distribution or designability. ProteinMPNN/refolding with positive controls is still required. No reference coordinates or locked tests used.

Across the two fixed seeds per family (four pairs per method), mean pairwise CA-lDDT: {'initial': 0.26555168902907755, 'guided': 0.32231820083560286, 'random': 0.2537916577597236}. This describes all outputs, not designable diversity.
