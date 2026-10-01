# Ensemble state and distribution diagnostics

Run: ensemble_49638012.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.2500 | 0.8523 | 0.3298 |
| cfg1/factorial | 8 | 4 | 1.0000 | 0.2500 | 0.8541 | 0.2493 |
| cfg1/latent | 8 | 4 | 1.0000 | 0.3750 | 0.8537 | 0.3018 |
| cfg2/decoder | 48 | 16 | 0.9876 | 0.2812 | 0.8656 | 0.4989 |
| cfg2/factorial | 48 | 16 | 0.9909 | 0.4062 | 0.8676 | 0.4851 |
| cfg2/latent | 48 | 16 | 0.9889 | 0.4062 | 0.8677 | 0.4844 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
