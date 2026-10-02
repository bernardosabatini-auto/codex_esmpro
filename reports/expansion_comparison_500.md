# Larger-corpus training capacity

Checkpoint500; 427 training families, fixed64-family diagnostic panel. Both seeds retained; exact target/label/LR schedules and initialization checked.

Every evaluated family is training data. Family intervals are unadjusted. This cannot establish external diversity or promote a model.

| Seed / training cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| 2026100171_all64 | 0.71907 | 0.48936 | 0.98535 | 0.90328 | 0.50672 |
| 2026100171_original32 | 0.72173 | 0.50789 | 0.98535 | 0.91501 | 0.50419 |
| 2026100171_new32 | 0.71641 | 0.47083 | 0.98535 | 0.89155 | 0.50924 |
| 2026100181_all64 | 0.70279 | 0.45032 | 0.99170 | 0.90604 | 0.51702 |
| 2026100181_original32 | 0.74464 | 0.49881 | 0.99316 | 0.91778 | 0.48762 |
| 2026100181_new32 | 0.66094 | 0.40182 | 0.99023 | 0.89430 | 0.54642 |

2026100171_all64_vs_initial: recall delta+0.01929,95% interval[-0.029842819940476193, 0.0681389508928571]; validity delta-0.00928.

2026100171_original32_vs_initial: recall delta-0.02574,95% interval[-0.10654761904761906, 0.047916666666666656]; validity delta-0.00684.

2026100171_new32_vs_initial: recall delta+0.06432,95% interval[0.007812499999999995, 0.12395833333333334]; validity delta-0.01172.

2026100181_all64_vs_initial: recall delta+0.00301,95% interval[-0.052161458333333334, 0.05628999255952378]; validity delta-0.00293.

2026100181_original32_vs_initial: recall delta-0.00283,95% interval[-0.07917782738095239, 0.07248139880952366]; validity delta+0.00098.

2026100181_new32_vs_initial: recall delta+0.00885,95% interval[-0.07188802083333334, 0.08645833333333333]; validity delta-0.00684.

Original32, seed2026100171, larger minus historical full122: recall-0.03542,95% interval[-0.11592261904761905, 0.044494047619047614]; validity-0.00977. Target draws differ across corpus sizes; this is a paired family diagnostic, not identical optimization streams.

Original32, seed2026100181, larger minus historical full122: recall-0.07917,95% interval[-0.15416666666666667, -0.008333333333333331]; validity+0.00195. Target draws differ across corpus sizes; this is a paired family diagnostic, not identical optimization streams.

Replicated declared capacity gate: False. Both checkpoints still require the separate unchanged native quality screen.
