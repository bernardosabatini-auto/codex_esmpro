> **Invalidated as a teacher comparison (October 1):** active missing MSA weights in the installed HF port. See [adapter audit](teacher_adapter_audit_20261001.md). Do not use these numbers for model selection.

# Teacher seed and integration-step diagnostic

Status: complete.

ESMFold2-Fast structure-only sampling with validated trunk reuse. Seeds are repeated draws, integration steps are not physical trajectory frames. Dispersion alone does not demonstrate state coverage.

Full-fold controls include the confidence head; production sampling timing excludes it. Thirty-two samples per target/setting, collected in fixed groups of eight.

| Steps | Mean pairwise CA RMSD (A) | Peptide outlier fraction | Structure sampling seconds |
|---|---:|---:|---:|
| 25 | 0.9311 | 0.0001 | 14.37 |
| 50 | 1.0759 | 0.0000 | 26.93 |
| 100 | 1.1557 | 0.0000 | 53.63 |
