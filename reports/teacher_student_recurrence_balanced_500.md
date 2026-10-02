# Student misses and fresh teacher recurrence

Post-hoc descriptive diagnosis on the unchanged32 training proteins and frozen teacher states. Both teachers and students draw32 samples, but their noise seeds are not paired across model types. Intervals pair sequence families only. Neither fresh teacher sampling nor student coverage establishes biological populations. No state is removed or reweighted by this analysis.

| Student / update / CFG | Teacher condition | Student recall | Fresh teacher recall | Student minus teacher | 95% family interval |
|---|---|---:|---:|---:|---|
| aligned_teacher_balanced_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| aligned_teacher_balanced_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| aligned_teacher_balanced_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| aligned_teacher_balanced_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| aligned_teacher_balanced_500_cfg1 | fixed_trunk | 0.89881 | 0.83661 | +0.06220 | [0.0010416666666666647, 0.12782738095238094] |
| aligned_teacher_balanced_500_cfg1 | new_trunk | 0.89881 | 0.85119 | +0.04762 | [-0.01875000000000001, 0.11666666666666667] |
| aligned_teacher_balanced_500_cfg2 | fixed_trunk | 0.72426 | 0.83661 | -0.11235 | [-0.21428943452380952, -0.010416666666666668] |
| aligned_teacher_balanced_500_cfg2 | new_trunk | 0.72426 | 0.85119 | -0.12693 | [-0.22380952380952382, -0.028995535714286053] |
| pca_teacher_balanced_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| pca_teacher_balanced_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| pca_teacher_balanced_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| pca_teacher_balanced_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| pca_teacher_balanced_500_cfg1 | fixed_trunk | 0.87589 | 0.83661 | +0.03929 | [-0.04017857142857144, 0.12083333333333333] |
| pca_teacher_balanced_500_cfg1 | new_trunk | 0.87589 | 0.85119 | +0.02470 | [-0.0625, 0.11220238095238097] |
| pca_teacher_balanced_500_cfg2 | fixed_trunk | 0.68199 | 0.83661 | -0.15461 | [-0.25357142857142856, -0.054758184523809594] |
| pca_teacher_balanced_500_cfg2 | new_trunk | 0.68199 | 0.85119 | -0.16920 | [-0.27158110119047624, -0.06413690476190477] |

Singleton states grouped by observed fresh-teacher recurrence. Counts pool states and are descriptive, not independent observations. A miss in both finite ensembles does not establish that a state cannot recur.

| Student / update / CFG | Teacher recurrence | States | Student states hit |
|---|---|---:|---:|
| aligned_teacher_balanced_0_cfg1 | singleton_both | 31 | 22 |
| aligned_teacher_balanced_0_cfg1 | singleton_fixed_only | 1 | 0 |
| aligned_teacher_balanced_0_cfg1 | singleton_neither | 17 | 5 |
| aligned_teacher_balanced_0_cfg1 | singleton_new_only | 2 | 0 |
| aligned_teacher_balanced_500_cfg1 | singleton_both | 31 | 26 |
| aligned_teacher_balanced_500_cfg1 | singleton_fixed_only | 1 | 1 |
| aligned_teacher_balanced_500_cfg1 | singleton_neither | 17 | 8 |
| aligned_teacher_balanced_500_cfg1 | singleton_new_only | 2 | 2 |
| pca_teacher_balanced_0_cfg1 | singleton_both | 31 | 22 |
| pca_teacher_balanced_0_cfg1 | singleton_fixed_only | 1 | 0 |
| pca_teacher_balanced_0_cfg1 | singleton_neither | 17 | 5 |
| pca_teacher_balanced_0_cfg1 | singleton_new_only | 2 | 0 |
| pca_teacher_balanced_500_cfg1 | singleton_both | 31 | 26 |
| pca_teacher_balanced_500_cfg1 | singleton_fixed_only | 1 | 1 |
| pca_teacher_balanced_500_cfg1 | singleton_neither | 17 | 9 |
| pca_teacher_balanced_500_cfg1 | singleton_new_only | 2 | 1 |
