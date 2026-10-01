# Teacher seed and integration-step diagnostic

Status: complete.

ESMFold2-Fast structure-only sampling with validated trunk reuse. Seeds are repeated draws, integration steps are not physical trajectory frames. Dispersion alone does not demonstrate state coverage.

Structure-only sampling reuses trunk, excludes confidence head. Full fold controls include confidence. Do not compare structure-only timing against full-fold timing as an end-to-end speedup.

Thirty-two samples per target/setting; batch 8, trunk realizations 1.

| Steps | Mean pairwise CA RMSD (A) | Peptide outlier fraction | Measured sampling seconds |
|---|---:|---:|---:|
| 25 | 0.9152 | 0.0001 | 14.50 |
| 50 | 1.0562 | 0.0000 | 27.16 |
| 100 | 1.1399 | 0.0000 | 54.08 |
