# Larger-corpus training capacity

Checkpoint2000; 427 training families, fixed64-family diagnostic panel. Both seeds retained; exact target/label/LR schedules and initialization checked.

Every evaluated family is training data. Family intervals are unadjusted. This cannot establish external diversity or promote a model.

| Seed / training cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| 2026100171_all64 | 0.78491 | 0.59275 | 0.99463 | 0.92795 | 0.46948 |
| 2026100171_original32 | 0.82842 | 0.63705 | 0.99414 | 0.93988 | 0.44722 |
| 2026100171_new32 | 0.74141 | 0.54844 | 0.99512 | 0.91601 | 0.49173 |
| 2026100181_all64 | 0.77439 | 0.60939 | 0.99365 | 0.92764 | 0.46362 |
| 2026100181_original32 | 0.80685 | 0.61696 | 0.99316 | 0.93839 | 0.43649 |
| 2026100181_new32 | 0.74193 | 0.60182 | 0.99414 | 0.91689 | 0.49076 |

2026100171_all64_vs_initial: recall delta+0.08514,95% interval[0.027399088541666665, 0.14388020833333331]; validity delta+0.00000.

2026100171_original32_vs_initial: recall delta+0.08095,95% interval[-0.004166666666666673, 0.16354166666666664]; validity delta+0.00195.

2026100171_new32_vs_initial: recall delta+0.08932,95% interval[0.010937500000000001, 0.1765625]; validity delta-0.00195.

2026100181_all64_vs_initial: recall delta+0.07461,95% interval[0.018749069940476187, 0.1308612351190476]; validity delta-0.00098.

2026100181_original32_vs_initial: recall delta+0.05937,95% interval[-0.030208333333333337, 0.146875]; validity delta+0.00098.

2026100181_new32_vs_initial: recall delta+0.08984,95% interval[0.021614583333333336, 0.16354817708333327]; validity delta-0.00293.

Original32, seed2026100171, larger minus historical full122: recall-0.02054,95% interval[-0.08898809523809526, 0.04613095238095238]; validity-0.00293. Target draws differ across corpus sizes; this is a paired family diagnostic, not identical optimization streams.

Original32, seed2026100181, larger minus historical full122: recall-0.04896,95% interval[-0.13854166666666667, 0.03541666666666668]; validity-0.00195. Target draws differ across corpus sizes; this is a paired family diagnostic, not identical optimization streams.

Replicated declared capacity gate: True. Both checkpoints still require the separate unchanged native quality screen.
