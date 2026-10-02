# Latent identity versus decoded state diagnostic

Primary CFG1; same32 training proteins and generated samples. Each model is compared with teacher latents in its own training frame. Latent identity is a permissive nearest-label assignment with no distance or validity threshold; it is not a valid-state hit or a substitute for structural evaluation. Coordinate pose can dominate latent distance, including for the same decoded shape. Consequently latent recalls cannot establish decoder causality or be compared across frames as quality scores. Teacher self-assignment is checked in each frame.

| Model / update | Latent nearest-label recall | Decoded valid recall | Identity agreement | Latent nearest RMSE | Latent singleton hits | Decoded singleton hits | Latent-only singletons | Decoded-only singletons |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| aligned_teacher_empirical_0 | 0.74821 | 0.74747 | 0.41992 | 0.44329 | 26/51 | 27/51 | 12 | 13 |
| aligned_teacher_empirical_500 | 0.71101 | 0.67932 | 0.76465 | 0.25700 | 22/51 | 21/51 | 10 | 9 |
| aligned_teacher_empirical_2000 | 0.66682 | 0.62500 | 0.86914 | 0.14643 | 20/51 | 15/51 | 10 | 5 |
| pca_teacher_empirical_0 | 0.84717 | 0.74747 | 0.43652 | 0.26249 | 35/51 | 27/51 | 17 | 9 |
| pca_teacher_empirical_500 | 0.73527 | 0.61310 | 0.82422 | 0.10385 | 28/51 | 16/51 | 19 | 7 |
| pca_teacher_empirical_2000 | 0.75193 | 0.66369 | 0.85742 | 0.09072 | 26/51 | 21/51 | 10 | 5 |

A state missing among32 samples has not been shown to have zero model probability. For a specified state with zero hits in32 independent draws, the exact one-sided95% upper bound is about0.0894, which exceeds the empirical singleton prior1/16. More samples would be needed to separate extremely low probability from zero. The matched32-sample coverage loss remains the relevant efficiency failure.
