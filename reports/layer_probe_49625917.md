# Matched ESMC layer probes

Status: complete.

512 training families and 64 tuning families. Matched 2561x8 ridge probes with per-token feature normalization and equal protein weighting. Sixty-four probe confirmation families remain unscored. This is a representation screen, not a generative-model comparison.

| Layer | Ridge | Tuning CA lDDT | Tuning CA RMSD | Latent MSE |
|---|---:|---:|---:|---:|
| 20 | 0.001 | 0.2089 | 21.843 | 0.6771 |
| 20 | 0.01 | 0.1787 | 21.739 | 0.6546 |
| 20 | 0.1 | 0.1180 | 21.856 | 0.6234 |
| 40 | 0.001 | 0.2130 | 21.962 | 0.6999 |
| 40 | 0.01 | 0.2021 | 21.879 | 0.6852 |
| 40 | 0.1 | 0.1508 | 21.845 | 0.6433 |
| 60 | 0.001 | 0.2322 | 21.402 | 0.7102 |
| 60 | 0.01 | 0.2307 | 21.379 | 0.7046 |
| 60 | 0.1 | 0.2119 | 21.306 | 0.6670 |
| 80 | 0.001 | 0.1679 | 22.427 | 0.6273 |
| 80 | 0.01 | 0.1625 | 22.427 | 0.6238 |
| 80 | 0.1 | 0.1249 | 22.470 | 0.6052 |

Ridge selection and paired differences use the tuning set, so they cannot establish confirmation or a generative-model improvement. Learned mixtures and full flow training require separate matched tests.
