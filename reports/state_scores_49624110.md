# Ensemble state and distribution diagnostics

Run: teacher_ensemble_49624110.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| steps100 | 8 | 4 | 1.0000 | 0.5000 | 0.9131 | 0.3313 |
| steps25 | 8 | 4 | 1.0000 | 0.5000 | 0.9146 | 0.3323 |
| steps50 | 8 | 4 | 1.0000 | 0.5000 | 0.9141 | 0.3309 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
