# Restricted versus full-network balanced adaptation

Checkpoint 2000; both seeds retained. Configurations, initial predictions, target/label/LR logs and frozen raw/EMA hashes verified. All cohorts are training data; biological diversity and generalization require separate evaluation.

| Seed / arm / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| 2026100171_full_all122 | 0.84711 | 0.75891 | 0.99641 | 0.95162 | 0.36774 |
| 2026100171_tail_all122 | 0.67493 | 0.42992 | 0.96593 | 0.86972 | 0.56757 |
| 2026100171_initial_all122 | 0.67562 | 0.41127 | 0.99206 | 0.86886 | 0.58185 |
| 2026100171_full_original32 | 0.84896 | 0.71548 | 0.99707 | 0.96181 | 0.38983 |
| 2026100171_tail_original32 | 0.73393 | 0.47738 | 0.96289 | 0.89848 | 0.50159 |
| 2026100171_initial_original32 | 0.74747 | 0.50446 | 0.99219 | 0.89842 | 0.51619 |
| 2026100171_full_additional90 | 0.84646 | 0.77435 | 0.99618 | 0.94799 | 0.35988 |
| 2026100171_tail_additional90 | 0.65396 | 0.41304 | 0.96701 | 0.85949 | 0.59104 |
| 2026100171_initial_additional90 | 0.65008 | 0.37813 | 0.99201 | 0.85835 | 0.60519 |
| 2026100181_full_all122 | 0.85787 | 0.78772 | 0.99718 | 0.95198 | 0.36814 |
| 2026100181_tail_all122 | 0.66223 | 0.42623 | 0.96619 | 0.87093 | 0.56408 |
| 2026100181_initial_all122 | 0.67562 | 0.41127 | 0.99206 | 0.86886 | 0.58185 |
| 2026100181_full_original32 | 0.85580 | 0.77381 | 0.99512 | 0.96374 | 0.40099 |
| 2026100181_tail_original32 | 0.72976 | 0.46071 | 0.95996 | 0.89979 | 0.49784 |
| 2026100181_initial_original32 | 0.74747 | 0.50446 | 0.99219 | 0.89842 | 0.51619 |
| 2026100181_full_additional90 | 0.85861 | 0.79267 | 0.99792 | 0.94780 | 0.35646 |
| 2026100181_tail_additional90 | 0.63821 | 0.41397 | 0.96840 | 0.86067 | 0.58763 |
| 2026100181_initial_additional90 | 0.65008 | 0.37813 | 0.99201 | 0.85835 | 0.60519 |

2026100171_tail_all122_vs_full: recall delta -0.17218, 95% interval [-0.22685719164715068, -0.11831381733021079]; validity delta -0.03048.

2026100171_tail_all122_vs_initial: recall delta -0.00069, 95% interval [-0.02070672326307572, 0.019135441061670568]; validity delta -0.02613.

2026100181_tail_all122_vs_full: recall delta -0.19565, 95% interval [-0.25005854800936766, -0.14194867291178767]; validity delta -0.03099.

2026100181_tail_all122_vs_initial: recall delta -0.01340, 95% interval [-0.03638807572209212, 0.008265027322404368]; validity delta -0.02587.
