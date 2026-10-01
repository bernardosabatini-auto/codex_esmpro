# Ensemble state and distribution diagnostics

Run: ensemble_49642986.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.3750 | 0.8473 | 0.3303 |
| cfg1/factorial | 8 | 4 | 1.0000 | 0.3750 | 0.8444 | 0.3217 |
| cfg1/latent | 8 | 4 | 0.9883 | 0.5000 | 0.8466 | 0.3198 |
| cfg2/decoder | 48 | 16 | 0.9792 | 0.2500 | 0.8622 | 0.4936 |
| cfg2/factorial | 48 | 16 | 0.9909 | 0.3750 | 0.8639 | 0.4814 |
| cfg2/latent | 48 | 16 | 0.9902 | 0.4375 | 0.8642 | 0.4802 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
