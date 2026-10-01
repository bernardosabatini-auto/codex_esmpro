# Ensemble state and distribution diagnostics

Run: ensemble_49647134.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 0.8750 | 0.2500 | 0.8479 | 1.0536 |
| cfg1/factorial | 8 | 4 | 0.9258 | 0.3750 | 0.8422 | 0.7211 |
| cfg1/latent | 8 | 4 | 0.9219 | 0.3750 | 0.8346 | 0.6852 |
| cfg2/decoder | 48 | 16 | 0.9792 | 0.2812 | 0.8649 | 0.4846 |
| cfg2/factorial | 48 | 16 | 0.9857 | 0.4062 | 0.8690 | 0.4702 |
| cfg2/latent | 48 | 16 | 0.9863 | 0.4375 | 0.8680 | 0.4613 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
