# Ensemble state and distribution diagnostics

Run: ensemble_49646851.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.2500 | 0.8568 | 0.3300 |
| cfg1/factorial | 8 | 4 | 1.0000 | 0.3750 | 0.8481 | 0.3504 |
| cfg1/latent | 8 | 4 | 0.9883 | 0.3750 | 0.8520 | 0.3257 |
| cfg2/decoder | 48 | 16 | 0.9596 | 0.2812 | 0.8656 | 0.4835 |
| cfg2/factorial | 48 | 16 | 0.9759 | 0.3750 | 0.8643 | 0.4777 |
| cfg2/latent | 48 | 16 | 0.9798 | 0.4062 | 0.8637 | 0.4757 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
