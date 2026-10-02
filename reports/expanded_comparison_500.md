# Replicated122-family teacher-prior comparison

Checkpoint500; matched configurations, schedules, within-seed target/LR logs and initialization predictions verified. Both declared seeds retained.

All cohorts below are training data, including the additional90 proteins. Teacher modes are predictions, not experimental states. Geometry failures remain in denominators. Intervals resample families and are unadjusted.

| Seed / prior / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV |
|---|---:|---:|---:|---:|---:|---:|
| 2026100171_empirical_all122 | 0.66636 | 0.52357 | 0.99539 | 0.92438 | 0.28429 | 0.53911 |
| 2026100171_balanced_all122 | 0.79403 | 0.64495 | 0.99283 | 0.92101 | 0.38364 | 0.44419 |
| 2026100171_empirical_original32 | 0.69018 | 0.53839 | 0.99512 | 0.94257 | 0.29688 | 0.50898 |
| 2026100171_balanced_original32 | 0.75714 | 0.57381 | 0.99512 | 0.93988 | 0.40723 | 0.44127 |
| 2026100171_empirical_additional90 | 0.65790 | 0.51829 | 0.99549 | 0.91791 | 0.27981 | 0.54983 |
| 2026100171_balanced_additional90 | 0.80714 | 0.67024 | 0.99201 | 0.91430 | 0.37525 | 0.44523 |
| 2026100181_empirical_all122 | 0.64805 | 0.52499 | 0.98847 | 0.92538 | 0.26778 | 0.53803 |
| 2026100181_balanced_all122 | 0.80796 | 0.65767 | 0.98924 | 0.92122 | 0.36494 | 0.43549 |
| 2026100181_empirical_original32 | 0.69673 | 0.55476 | 0.98633 | 0.93992 | 0.30176 | 0.50942 |
| 2026100181_balanced_original32 | 0.82381 | 0.64226 | 0.99121 | 0.93723 | 0.38770 | 0.42186 |
| 2026100181_empirical_additional90 | 0.63074 | 0.51440 | 0.98924 | 0.92020 | 0.25569 | 0.54820 |
| 2026100181_balanced_additional90 | 0.80233 | 0.66315 | 0.98854 | 0.91552 | 0.35685 | 0.44034 |

| Full122 balanced comparison | Recall difference |95% interval | Validity difference |
|---|---:|---|---:|
| 2026100171_balanced_all122_vs_initial | +0.11840 | [0.06818867096018734, 0.16872609289617485] | +0.00077 |
| 2026100171_balanced_all122_vs_empirical | +0.12766 | [0.08622145784543325, 0.168170862607338] | -0.00256 |
| 2026100181_balanced_all122_vs_initial | +0.13234 | [0.08067915690866509, 0.18487534153005467] | -0.00282 |
| 2026100181_balanced_all122_vs_empirical | +0.15991 | [0.11396370023419204, 0.20677351678376268] | +0.00077 |

Seed2026100171 capacity criteria: True; {'positive_recall_ci_vs_initial': True, 'positive_recall_ci_vs_empirical': True, 'validity_vs_initial': True, 'validity_vs_empirical': True}.

Seed2026100181 capacity criteria: True; {'positive_recall_ci_vs_initial': True, 'positive_recall_ci_vs_empirical': True, 'validity_vs_initial': True, 'validity_vs_empirical': True}.

Replicated capacity criteria passed: True.
Separate accuracy, experimental-state ensemble coverage and matched timing remain required; this training-data analysis cannot promote a model. The broader criteria do not replace the original32/reference-control gate.
