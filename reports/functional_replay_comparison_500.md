# Functional replay capacity retention

Checkpoint500; both matched427-family seeds, unchanged64-family training panel. Primary recipes, target/label/LR draws, initialization and frozen-reference controls verified. Retains capacity at both seeds:True.

All families are training data. No native or external qualification follows from capacity alone.

| Seed / cohort / model | Recall@32 | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|
| 2026100171_all64_full | 0.71907 | 0.98535 | 0.90328 | 0.50672 |
| 2026100171_all64_replay | 0.71125 | 0.99072 | 0.90256 | 0.50789 |
| 2026100171_all64_initial | 0.69978 | 0.99463 | 0.88532 | 0.57040 |
| 2026100171_original32_full | 0.72173 | 0.98535 | 0.91501 | 0.50419 |
| 2026100171_original32_replay | 0.71652 | 0.99316 | 0.91512 | 0.49247 |
| 2026100171_original32_initial | 0.74747 | 0.99219 | 0.89842 | 0.51619 |
| 2026100171_new32_full | 0.71641 | 0.98535 | 0.89155 | 0.50924 |
| 2026100171_new32_replay | 0.70599 | 0.98828 | 0.89000 | 0.52331 |
| 2026100171_new32_initial | 0.65208 | 0.99707 | 0.87222 | 0.62461 |
| 2026100181_all64_full | 0.70279 | 0.99170 | 0.90604 | 0.51702 |
| 2026100181_all64_replay | 0.70394 | 0.99219 | 0.90331 | 0.51995 |
| 2026100181_all64_initial | 0.69978 | 0.99463 | 0.88532 | 0.57040 |
| 2026100181_original32_full | 0.74464 | 0.99316 | 0.91778 | 0.48762 |
| 2026100181_original32_replay | 0.74435 | 0.99219 | 0.91533 | 0.49114 |
| 2026100181_original32_initial | 0.74747 | 0.99219 | 0.89842 | 0.51619 |
| 2026100181_new32_full | 0.66094 | 0.99023 | 0.89430 | 0.54642 |
| 2026100181_new32_replay | 0.66354 | 0.99219 | 0.89129 | 0.54876 |
| 2026100181_new32_initial | 0.65208 | 0.99707 | 0.87222 | 0.62461 |

2026100171_all64_vs_full: recall delta-0.00781, paired family95% interval[-0.03489583333333333, 0.01666666666666667]; validity delta+0.00537.

2026100171_all64_vs_initial: recall delta+0.01148, paired family95% interval[-0.03791480654761905, 0.060585472470238065]; validity delta-0.00391.

2026100181_all64_vs_full: recall delta+0.00115, paired family95% interval[-0.029057849702380952, 0.032552083333333336]; validity delta+0.00049.

2026100181_all64_vs_initial: recall delta+0.00417, paired family95% interval[-0.041966145833333336, 0.049109002976190454]; validity delta-0.00244.
