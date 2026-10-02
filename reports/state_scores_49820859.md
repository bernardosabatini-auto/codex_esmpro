# Ensemble state and distribution diagnostics

Run: ensemble_49820859.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 48 | 16 | 1.0000 | 0.2188 | 0.8680 | 0.4941 |
| cfg1/factorial | 48 | 16 | 1.0000 | 0.3750 | 0.8671 | 0.4828 |
| cfg1/latent | 48 | 16 | 0.9987 | 0.4375 | 0.8674 | 0.4880 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
