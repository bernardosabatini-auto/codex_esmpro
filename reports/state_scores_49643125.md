# Ensemble state and distribution diagnostics

Run: ensemble_49643125.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.2500 | 0.8436 | 0.3271 |
| cfg1/factorial | 8 | 4 | 0.9844 | 0.3750 | 0.8364 | 0.2309 |
| cfg1/latent | 8 | 4 | 0.9727 | 0.3750 | 0.8376 | 0.2384 |
| cfg2/decoder | 48 | 16 | 1.0000 | 0.2812 | 0.8642 | 0.4787 |
| cfg2/factorial | 48 | 16 | 0.9922 | 0.4062 | 0.8667 | 0.4763 |
| cfg2/latent | 48 | 16 | 0.9915 | 0.4375 | 0.8671 | 0.4760 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
