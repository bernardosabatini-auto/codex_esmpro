# Replicated122-family teacher-prior comparison

Checkpoint2000; matched configurations, schedules, within-seed target/LR logs and initialization predictions verified. Both declared seeds retained.

All cohorts below are training data, including the additional90 proteins. Teacher modes are predictions, not experimental states. Geometry failures remain in denominators. Intervals resample families and are unadjusted.

| Seed / prior / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV |
|---|---:|---:|---:|---:|---:|---:|
| 2026100171_empirical_all122 | 0.57427 | 0.50685 | 0.99744 | 0.95473 | 0.20348 | 0.55060 |
| 2026100171_balanced_all122 | 0.84711 | 0.75891 | 0.99641 | 0.95162 | 0.36289 | 0.36774 |
| 2026100171_empirical_original32 | 0.62812 | 0.53140 | 0.99609 | 0.96359 | 0.24414 | 0.53546 |
| 2026100171_balanced_original32 | 0.84896 | 0.71548 | 0.99707 | 0.96181 | 0.35645 | 0.38983 |
| 2026100171_empirical_additional90 | 0.55512 | 0.49812 | 0.99792 | 0.95159 | 0.18903 | 0.55598 |
| 2026100171_balanced_additional90 | 0.84646 | 0.77435 | 0.99618 | 0.94799 | 0.36519 | 0.35988 |
| 2026100181_empirical_all122 | 0.59147 | 0.52995 | 0.99565 | 0.95444 | 0.19964 | 0.53730 |
| 2026100181_balanced_all122 | 0.85787 | 0.78772 | 0.99718 | 0.95198 | 0.36984 | 0.36814 |
| 2026100181_empirical_original32 | 0.62009 | 0.55268 | 0.99707 | 0.96614 | 0.22852 | 0.51483 |
| 2026100181_balanced_original32 | 0.85580 | 0.77381 | 0.99512 | 0.96374 | 0.38574 | 0.40099 |
| 2026100181_empirical_additional90 | 0.58130 | 0.52187 | 0.99514 | 0.95028 | 0.18937 | 0.54529 |
| 2026100181_balanced_additional90 | 0.85861 | 0.79267 | 0.99792 | 0.94780 | 0.36419 | 0.35646 |

| Full122 balanced comparison | Recall difference |95% interval | Validity difference |
|---|---:|---|---:|
| 2026100171_balanced_all122_vs_initial | +0.17149 | [0.11759196916471505, 0.22596701795472288] | +0.00435 |
| 2026100171_balanced_all122_vs_empirical | +0.27284 | [0.23074721896955505, 0.3152629781420765] | -0.00102 |
| 2026100181_balanced_all122_vs_initial | +0.18225 | [0.12840481069476972, 0.23790007806401245] | +0.00512 |
| 2026100181_balanced_all122_vs_empirical | +0.26640 | [0.2230386416861827, 0.3093103532396565] | +0.00154 |

Seed2026100171 capacity criteria: True; {'positive_recall_ci_vs_initial': True, 'positive_recall_ci_vs_empirical': True, 'validity_vs_initial': True, 'validity_vs_empirical': True}.

Seed2026100181 capacity criteria: True; {'positive_recall_ci_vs_initial': True, 'positive_recall_ci_vs_empirical': True, 'validity_vs_initial': True, 'validity_vs_empirical': True}.

Replicated capacity criteria passed: True.
Separate accuracy, experimental-state ensemble coverage and matched timing remain required; this training-data analysis cannot promote a model. The broader criteria do not replace the original32/reference-control gate.
