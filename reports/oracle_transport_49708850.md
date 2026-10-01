# Oracle flow and decoder positive control

Status: complete.

This vector field knows the complete empirical teacher latent distribution for each training protein. It is not deployable prediction and cannot establish learned-model accuracy. Same fresh32 Gaussian seeds and decoder seeds as the capacity test; ordinary Euler integration, latent layer normalization and3-step decoding.

| Frame / steps | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | State TV | Ideal teacher recall @32 |
|---|---:|---:|---:|---:|---:|---:|
| aligned_5 | 0.90714 | 0.90714 | 0.99707 | 0.99855 | 0.07617 | 0.94512 |
| aligned_10 | 0.95804 | 0.95804 | 0.99902 | 0.99884 | 0.05664 | 0.94512 |
| aligned_25 | 0.96920 | 0.96920 | 0.99902 | 0.99886 | 0.06055 | 0.94512 |
| aligned_100 | 0.96920 | 0.96920 | 0.99902 | 0.99885 | 0.06543 | 0.94512 |
| pca_5 | 0.80074 | 0.80074 | 0.99902 | 0.99866 | 0.09277 | 0.94512 |
| pca_10 | 0.91994 | 0.91994 | 0.99902 | 0.99890 | 0.07617 | 0.94512 |
| pca_25 | 0.91949 | 0.91949 | 0.99902 | 0.99895 | 0.07422 | 0.94512 |
| pca_100 | 0.92396 | 0.92396 | 0.99902 | 0.99896 | 0.07324 | 0.94512 |
