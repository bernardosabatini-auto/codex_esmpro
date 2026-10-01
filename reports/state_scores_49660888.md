# Ensemble state and distribution diagnostics

Run: ensemble_49660888.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.1250 | 0.8395 | 0.3257 |
| cfg1/factorial | 8 | 4 | 0.9688 | 0.3750 | 0.8212 | 0.3219 |
| cfg1/latent | 8 | 4 | 0.9727 | 0.3750 | 0.8312 | 0.3180 |
| cfg2/decoder | 48 | 16 | 0.9974 | 0.2500 | 0.8647 | 0.4932 |
| cfg2/factorial | 48 | 16 | 0.9948 | 0.4062 | 0.8663 | 0.4810 |
| cfg2/latent | 48 | 16 | 0.9928 | 0.4688 | 0.8663 | 0.4760 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
