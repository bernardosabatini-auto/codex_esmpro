# Ensemble state and distribution diagnostics

Run: ensemble_49640046.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg2/decoder | 48 | 16 | 0.9792 | 0.2812 | 0.8485 | 0.4976 |
| cfg2/factorial | 48 | 16 | 0.9863 | 0.3438 | 0.8504 | 0.4888 |
| cfg2/latent | 48 | 16 | 0.9850 | 0.4062 | 0.8501 | 0.4826 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
