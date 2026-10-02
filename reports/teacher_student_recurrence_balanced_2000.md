# Student misses and fresh teacher recurrence

Post-hoc descriptive diagnosis on the unchanged32 training proteins and frozen teacher states. Both teachers and students draw32 samples, but their noise seeds are not paired across model types. Intervals pair sequence families only. Neither fresh teacher sampling nor student coverage establishes biological populations. No state is removed or reweighted by this analysis.

| Student / update / CFG | Teacher condition | Student recall | Fresh teacher recall | Student minus teacher | 95% family interval |
|---|---|---:|---:|---:|---|
| aligned_teacher_balanced_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| aligned_teacher_balanced_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| aligned_teacher_balanced_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| aligned_teacher_balanced_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| aligned_teacher_balanced_2000_cfg1 | fixed_trunk | 0.89360 | 0.83661 | +0.05699 | [-0.027083333333333334, 0.14092261904761905] |
| aligned_teacher_balanced_2000_cfg1 | new_trunk | 0.89360 | 0.85119 | +0.04241 | [-0.045390625000000004, 0.1302157738095237] |
| aligned_teacher_balanced_2000_cfg2 | fixed_trunk | 0.72738 | 0.83661 | -0.10923 | [-0.21696428571428572, 0.007593005952380911] |
| aligned_teacher_balanced_2000_cfg2 | new_trunk | 0.72738 | 0.85119 | -0.12381 | [-0.22902901785714286, -0.009226190476190478] |
| pca_teacher_balanced_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| pca_teacher_balanced_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| pca_teacher_balanced_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| pca_teacher_balanced_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| pca_teacher_balanced_2000_cfg1 | fixed_trunk | 0.85610 | 0.83661 | +0.01949 | [-0.05208333333333333, 0.09062500000000001] |
| pca_teacher_balanced_2000_cfg1 | new_trunk | 0.85610 | 0.85119 | +0.00491 | [-0.06830357142857142, 0.07782738095238095] |
| pca_teacher_balanced_2000_cfg2 | fixed_trunk | 0.70134 | 0.83661 | -0.13527 | [-0.2363095238095238, -0.033924851190476245] |
| pca_teacher_balanced_2000_cfg2 | new_trunk | 0.70134 | 0.85119 | -0.14985 | [-0.25104166666666666, -0.05104166666666667] |

Singleton states grouped by observed fresh-teacher recurrence. Counts pool states and are descriptive, not independent observations. A miss in both finite ensembles does not establish that a state cannot recur.

| Student / update / CFG | Teacher recurrence | States | Student states hit |
|---|---|---:|---:|
| aligned_teacher_balanced_0_cfg1 | singleton_both | 31 | 22 |
| aligned_teacher_balanced_0_cfg1 | singleton_fixed_only | 1 | 0 |
| aligned_teacher_balanced_0_cfg1 | singleton_neither | 17 | 5 |
| aligned_teacher_balanced_0_cfg1 | singleton_new_only | 2 | 0 |
| aligned_teacher_balanced_2000_cfg1 | singleton_both | 31 | 26 |
| aligned_teacher_balanced_2000_cfg1 | singleton_fixed_only | 1 | 1 |
| aligned_teacher_balanced_2000_cfg1 | singleton_neither | 17 | 12 |
| aligned_teacher_balanced_2000_cfg1 | singleton_new_only | 2 | 1 |
| pca_teacher_balanced_0_cfg1 | singleton_both | 31 | 22 |
| pca_teacher_balanced_0_cfg1 | singleton_fixed_only | 1 | 0 |
| pca_teacher_balanced_0_cfg1 | singleton_neither | 17 | 5 |
| pca_teacher_balanced_0_cfg1 | singleton_new_only | 2 | 0 |
| pca_teacher_balanced_2000_cfg1 | singleton_both | 31 | 26 |
| pca_teacher_balanced_2000_cfg1 | singleton_fixed_only | 1 | 1 |
| pca_teacher_balanced_2000_cfg1 | singleton_neither | 17 | 9 |
| pca_teacher_balanced_2000_cfg1 | singleton_new_only | 2 | 1 |
