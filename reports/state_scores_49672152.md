# Ensemble state and distribution diagnostics

Run: ensemble_49672152.

Development contact-state coverage and MD distributions; no independent-generalization claim.

Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.

| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |
|---|---:|---:|---:|---:|---:|---:|
| cfg1/decoder | 8 | 4 | 1.0000 | 0.1250 | 0.8460 | 0.3286 |
| cfg1/factorial | 8 | 4 | 0.9922 | 0.2500 | 0.8515 | 0.3275 |
| cfg1/latent | 8 | 4 | 0.9922 | 0.3750 | 0.8496 | 0.3099 |
| cfg2/decoder | 48 | 16 | 1.0000 | 0.3438 | 0.8653 | 0.4971 |
| cfg2/factorial | 48 | 16 | 0.9863 | 0.4688 | 0.8642 | 0.4782 |
| cfg2/latent | 48 | 16 | 0.9883 | 0.4688 | 0.8640 | 0.4816 |

MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.
