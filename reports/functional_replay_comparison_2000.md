# Functional replay capacity retention

Checkpoint2000; both matched427-family seeds, unchanged64-family training panel. Primary recipes, target/label/LR draws, initialization and frozen-reference controls verified. Retains capacity at both seeds:False.

All families are training data. No native or external qualification follows from capacity alone.

| Seed / cohort / model | Recall@32 | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|
| 2026100171_all64_full | 0.78491 | 0.99463 | 0.92795 | 0.46948 |
| 2026100171_all64_replay | 0.77202 | 0.99463 | 0.92380 | 0.47022 |
| 2026100171_all64_initial | 0.69978 | 0.99463 | 0.88532 | 0.57040 |
| 2026100171_original32_full | 0.82842 | 0.99414 | 0.93988 | 0.44722 |
| 2026100171_original32_replay | 0.81384 | 0.99316 | 0.93638 | 0.43308 |
| 2026100171_original32_initial | 0.74747 | 0.99219 | 0.89842 | 0.51619 |
| 2026100171_new32_full | 0.74141 | 0.99512 | 0.91601 | 0.49173 |
| 2026100171_new32_replay | 0.73021 | 0.99609 | 0.91122 | 0.50736 |
| 2026100171_new32_initial | 0.65208 | 0.99707 | 0.87222 | 0.62461 |
| 2026100181_all64_full | 0.77439 | 0.99365 | 0.92764 | 0.46362 |
| 2026100181_all64_replay | 0.75539 | 0.99414 | 0.92346 | 0.47854 |
| 2026100181_all64_initial | 0.69978 | 0.99463 | 0.88532 | 0.57040 |
| 2026100181_original32_full | 0.80685 | 0.99316 | 0.93839 | 0.43649 |
| 2026100181_original32_replay | 0.81339 | 0.99414 | 0.93470 | 0.44523 |
| 2026100181_original32_initial | 0.74747 | 0.99219 | 0.89842 | 0.51619 |
| 2026100181_new32_full | 0.74193 | 0.99414 | 0.91689 | 0.49076 |
| 2026100181_new32_replay | 0.69740 | 0.99414 | 0.91221 | 0.51185 |
| 2026100181_new32_initial | 0.65208 | 0.99707 | 0.87222 | 0.62461 |

2026100171_all64_vs_full: recall delta-0.01289, paired family95% interval[-0.04261718750000001, 0.01266834077380951]; validity delta+0.00000.

2026100171_all64_vs_initial: recall delta+0.07225, paired family95% interval[0.01569940476190476, 0.12864769345238095]; validity delta+0.00000.

2026100181_all64_vs_full: recall delta-0.01899, paired family95% interval[-0.05234561011904761, 0.013076636904761905]; validity delta+0.00049.

2026100181_all64_vs_initial: recall delta+0.05562, paired family95% interval[0.004315476190476189, 0.10654761904761906]; validity delta-0.00049.
