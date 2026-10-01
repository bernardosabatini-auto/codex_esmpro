# Ensemble state and distribution diagnostics

Run: ensemble_49640022.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg2/decoder | 48 | 16 | 0.7533 | 0.1875 | 0.8063 | 0.5139 |
| cfg2/factorial | 48 | 16 | 0.7845 | 0.3750 | 0.8021 | 0.4562 |
| cfg2/latent | 48 | 16 | 0.7839 | 0.4062 | 0.8013 | 0.4550 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
