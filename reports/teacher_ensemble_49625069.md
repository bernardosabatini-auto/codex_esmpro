# Teacher seed and integration-step diagnostic

Status: complete.

ESMFold2-Fast structure-only sampling with validated trunk reuse. Seeds are repeated draws, integration steps are not physical trajectory frames. Dispersion alone does not demonstrate state coverage.

ESMC cached once per target; production includes stochastic trunk and structure sampling, excludes confidence. Numerical controls include full fold.

Thirty-two samples per target/setting; batch 4, trunk realizations 8.

| Steps | Mean pairwise CA RMSD (A) | Peptide outlier fraction | Measured sampling seconds |
|---|---:|---:|---:|
| 50 | 1.0757 | 0.0000 | 93.66 |
