# Teacher seed and integration-step diagnostic

Status: complete.

ESMFold2-Fast structure-only sampling with validated trunk reuse. Seeds are repeated draws, integration steps are not physical trajectory frames. Dispersion alone does not demonstrate state coverage.

Structure-only sampling reuses trunk, excludes confidence head. Full fold controls include confidence. Do not compare structure-only timing against full-fold timing as an end-to-end speedup.

128 samples per target/setting; batch 16, trunk realizations 1.

| Steps | Mean pairwise CA RMSD (A) | Peptide outlier fraction | Measured sampling seconds |
|---|---:|---:|---:|
| 50 | 2.6091 | 0.0000 | 261.34 |
