# Balanced teacher-label training exposure

Training exposure diagnostic, not a causal training-duration comparison or an authorization for longer runs.

Per-update bucket probabilities follow family counts. Batches vary by length; raw draws are therefore not the same as influence in the protein-mean loss. Gradient mass below sums each example weight1/batch-size before learning-rate scaling, clipping and adaptive optimization. Its total equals updates; it does not estimate actual parameter displacement.

| Run / updates | Families | Total draws | Median draws/family | Median gradient mass | Families missing a state |
|---|---:|---:|---:|---:|---:|
| overfit_49753133_500 | 122 | 6880 | 67.0 | 4.188 | 1 |
| overfit_49753133_2000 | 122 | 26680 | 258.0 | 16.188 | 0 |
| overfit_49753251_500 | 122 | 7000 | 66.0 | 4.125 | 0 |
| overfit_49753251_2000 | 122 | 27816 | 263.0 | 16.438 | 0 |
| overfit_49814858_500 | 427 | 6560 | 19.0 | 1.250 | 92 |
| overfit_49814858_2000 | 427 | 25192 | 73.0 | 4.625 | 1 |
| overfit_49815018_500 | 427 | 6496 | 18.0 | 1.125 | 71 |
| overfit_49815018_2000 | 427 | 26144 | 75.0 | 4.688 | 1 |

Same update counts do not give the same optimization exposure per family across corpus sizes. More examples per family would require additional training; whether that improves unseen valid diversity remains untested. All reconstructed target/label/LR logs must match their recorded runs.
