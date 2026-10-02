# Reconstruction bounds for the122-protein cohort

Conservative bounds for the existing fixed-noise aligned reconstruction audit only. This is not a fresh decoder audit, confidence interval or guarantee for all noise seeds. No student-dependent selection, new labels or training execution.

The metadata rule exactly reproduces the original32 selections and identifies90 additional training proteins. Every candidate refers to the same hash-bound label arrays as the completed512-protein audit. Each decoder failure is pessimistically assigned to a highest-weight valid teacher label; the per-protein minimum CA-lDDT bounds every weighted average. Invalid source labels have zero sampling weight. Average bounds weight proteins equally.

| Padded length | Proteins | Decoded failures | CA-lDDT lower bound | Empirical-prior validity lower bound | Balanced-prior validity lower bound |
|---|---:|---:|---:|---:|---:|
| all | 122 | 2 | 0.999375 | 0.998941 | 0.995219 |
| 128 | 5 | 0 | 0.999137 | 1.000000 | 1.000000 |
| 256 | 70 | 1 | 0.999354 | 0.999107 | 0.995238 |
| 384 | 25 | 1 | 0.999431 | 0.997333 | 0.990000 |
| 512 | 22 | 0 | 0.999428 | 1.000000 | 1.000000 |

Existing reconstruction margins passed conservatively: True.

These bounds permit reusing the existing aligned labels for a future matched prior experiment if the transfer decision supports expansion. They do not certify PCA labels, changed decoder weights/code, other random decoder seeds or student generalization. The122-family cohort has5/70/25/22 targets by length bucket; any broader training must account for that imbalance explicitly. No larger training run is launched by this certificate.
