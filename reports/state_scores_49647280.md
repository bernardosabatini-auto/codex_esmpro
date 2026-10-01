# Ensemble state and distribution diagnostics

Run: ensemble_49647280.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 0.8750 | 0.2500 | 0.8480 | 1.5028 |
| cfg1/factorial | 8 | 4 | 0.9258 | 0.3750 | 0.8375 | 1.0583 |
| cfg1/latent | 8 | 4 | 0.9219 | 0.3750 | 0.8279 | 0.8723 |
| cfg2/decoder | 48 | 16 | 0.9792 | 0.2812 | 0.8648 | 0.4867 |
| cfg2/factorial | 48 | 16 | 0.9857 | 0.4062 | 0.8685 | 0.4755 |
| cfg2/latent | 48 | 16 | 0.9876 | 0.4375 | 0.8676 | 0.4663 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
