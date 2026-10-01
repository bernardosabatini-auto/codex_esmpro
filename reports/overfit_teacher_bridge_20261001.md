# Teacher-frame Gaussian-bridge diagnostic

Uniform finite teacher labels plus Gaussian bridge noise, conditional on knowing the target protein. Training-label diagnostic only; not learned accuracy, state coverage or biological populations. Both frames use identical Gaussian draws. Reported velocity MSE floor is posterior latent variance divided by (1-t)^2 per coordinate, averaged over simulated bridges.

| Frame | Time | Oracle state accuracy | True-state posterior | State entropy (bits) | Velocity MSE floor |
|---|---:|---:|---:|---:|---:|
| aligned | 0.000 | 0.75586 | 0.64111 | 0.97594 | 0.007592 |
| aligned | 0.010 | 0.75488 | 0.64107 | 0.97585 | 0.007670 |
| aligned | 0.025 | 0.75513 | 0.64129 | 0.97402 | 0.007548 |
| aligned | 0.050 | 0.75562 | 0.64250 | 0.96625 | 0.006969 |
| aligned | 0.100 | 0.75476 | 0.64941 | 0.93361 | 0.005652 |
| aligned | 0.250 | 0.79871 | 0.70667 | 0.74752 | 0.003637 |
| aligned | 0.500 | 0.89539 | 0.84979 | 0.36932 | 0.002074 |
| aligned | 0.750 | 0.98804 | 0.98226 | 0.04539 | 0.000730 |
| aligned | 0.900 | 0.99976 | 0.99979 | 0.00057 | 0.000238 |
| aligned | 0.950 | 1.00000 | 1.00000 | 0.00000 | 0.000044 |
| aligned | 0.990 | 1.00000 | 1.00000 | 0.00000 | 0.000000 |
| pca | 0.000 | 0.75586 | 0.64111 | 0.97594 | 0.086632 |
| pca | 0.010 | 0.75586 | 0.64195 | 0.97128 | 0.084422 |
| pca | 0.025 | 0.75745 | 0.64624 | 0.94880 | 0.069598 |
| pca | 0.050 | 0.76538 | 0.65813 | 0.89571 | 0.039397 |
| pca | 0.100 | 0.78137 | 0.68494 | 0.80819 | 0.013255 |
| pca | 0.250 | 0.82959 | 0.75395 | 0.61553 | 0.003629 |
| pca | 0.500 | 0.91858 | 0.87871 | 0.29751 | 0.001912 |
| pca | 0.750 | 0.99023 | 0.98565 | 0.03471 | 0.000611 |
| pca | 0.900 | 0.99988 | 0.99981 | 0.00053 | 0.000186 |
| pca | 0.950 | 1.00000 | 1.00000 | 0.00000 | 0.000030 |
| pca | 0.990 | 1.00000 | 1.00000 | 0.00000 | 0.000000 |
