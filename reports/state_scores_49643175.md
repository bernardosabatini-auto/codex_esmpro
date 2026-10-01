# Ensemble state and distribution diagnostics

Run: ensemble_49643175.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 0.9297 | 0.2500 | 0.8388 | 0.3268 |
| cfg1/factorial | 8 | 4 | 0.9648 | 0.3750 | 0.8318 | 0.2390 |
| cfg1/latent | 8 | 4 | 0.9531 | 0.3750 | 0.8299 | 0.2375 |
| cfg2/decoder | 48 | 16 | 1.0000 | 0.2812 | 0.8651 | 0.4787 |
| cfg2/factorial | 48 | 16 | 0.9922 | 0.4062 | 0.8670 | 0.4761 |
| cfg2/latent | 48 | 16 | 0.9909 | 0.4062 | 0.8671 | 0.4703 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
