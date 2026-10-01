# Ensemble state and distribution diagnostics

Run: ensemble_49643056.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.2500 | 0.8429 | 0.3289 |
| cfg1/factorial | 8 | 4 | 1.0000 | 0.3750 | 0.8423 | 0.3213 |
| cfg1/latent | 8 | 4 | 0.9922 | 0.3750 | 0.8455 | 0.3202 |
| cfg2/decoder | 48 | 16 | 0.9766 | 0.2812 | 0.8619 | 0.4816 |
| cfg2/factorial | 48 | 16 | 0.9870 | 0.4062 | 0.8639 | 0.4777 |
| cfg2/latent | 48 | 16 | 0.9896 | 0.4375 | 0.8645 | 0.4773 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
