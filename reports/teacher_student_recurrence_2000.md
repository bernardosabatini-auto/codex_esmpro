# Student misses and fresh teacher recurrence

Post-hoc descriptive diagnosis on the unchanged32 training proteins and frozen teacher states. Both teachers and students draw32 samples, but their noise seeds are not paired across model types. Intervals pair sequence families only. Neither fresh teacher sampling nor student coverage establishes biological populations. No state is removed or reweighted by this analysis.

| Student / update / CFG | Teacher condition | Student recall | Fresh teacher recall | Student minus teacher | 95% family interval |
|---|---|---:|---:|---:|---|
| reference_empirical_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| reference_empirical_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| reference_empirical_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| reference_empirical_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| reference_empirical_2000_cfg1 | fixed_trunk | 0.37262 | 0.83661 | -0.46399 | [-0.5398809523809525, -0.38511904761904764] |
| reference_empirical_2000_cfg1 | new_trunk | 0.37262 | 0.85119 | -0.47857 | [-0.5686011904761905, -0.3895833333333333] |
| reference_empirical_2000_cfg2 | fixed_trunk | 0.36190 | 0.83661 | -0.47470 | [-0.5540215773809524, -0.3959784226190477] |
| reference_empirical_2000_cfg2 | new_trunk | 0.36190 | 0.85119 | -0.48929 | [-0.5819940476190477, -0.4002938988095239] |
| aligned_teacher_empirical_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| aligned_teacher_empirical_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| aligned_teacher_empirical_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| aligned_teacher_empirical_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| aligned_teacher_empirical_2000_cfg1 | fixed_trunk | 0.62500 | 0.83661 | -0.21161 | [-0.3150334821428572, -0.10475074404761921] |
| aligned_teacher_empirical_2000_cfg1 | new_trunk | 0.62500 | 0.85119 | -0.22619 | [-0.3370535714285714, -0.11219866071428578] |
| aligned_teacher_empirical_2000_cfg2 | fixed_trunk | 0.45238 | 0.83661 | -0.38423 | [-0.4555059523809524, -0.30832961309523815] |
| aligned_teacher_empirical_2000_cfg2 | new_trunk | 0.45238 | 0.85119 | -0.39881 | [-0.47455357142857146, -0.317109375] |
| pca_teacher_empirical_0_cfg1 | fixed_trunk | 0.74747 | 0.83661 | -0.08914 | [-0.16830357142857144, -0.009970238095238091] |
| pca_teacher_empirical_0_cfg1 | new_trunk | 0.74747 | 0.85119 | -0.10372 | [-0.18646205357142856, -0.020833333333333332] |
| pca_teacher_empirical_0_cfg2 | fixed_trunk | 0.56741 | 0.83661 | -0.26920 | [-0.37336681547619055, -0.16711309523809523] |
| pca_teacher_empirical_0_cfg2 | new_trunk | 0.56741 | 0.85119 | -0.28378 | [-0.38393229166666676, -0.18377976190476192] |
| pca_teacher_empirical_2000_cfg1 | fixed_trunk | 0.66369 | 0.83661 | -0.17292 | [-0.2791666666666667, -0.06250000000000001] |
| pca_teacher_empirical_2000_cfg1 | new_trunk | 0.66369 | 0.85119 | -0.18750 | [-0.30208333333333337, -0.07187500000000001] |
| pca_teacher_empirical_2000_cfg2 | fixed_trunk | 0.48571 | 0.83661 | -0.35089 | [-0.43928943452380953, -0.2525297619047619] |
| pca_teacher_empirical_2000_cfg2 | new_trunk | 0.48571 | 0.85119 | -0.36548 | [-0.4543154761904762, -0.2680059523809524] |

Singleton states grouped by observed fresh-teacher recurrence. Counts pool states and are descriptive, not independent observations. A miss in both finite ensembles does not establish that a state cannot recur.

| Student / update / CFG | Teacher recurrence | States | Student states hit |
|---|---|---:|---:|
| reference_empirical_0_cfg1 | singleton_both | 31 | 22 |
| reference_empirical_0_cfg1 | singleton_fixed_only | 1 | 0 |
| reference_empirical_0_cfg1 | singleton_neither | 17 | 5 |
| reference_empirical_0_cfg1 | singleton_new_only | 2 | 0 |
| reference_empirical_2000_cfg1 | singleton_both | 31 | 7 |
| reference_empirical_2000_cfg1 | singleton_fixed_only | 1 | 0 |
| reference_empirical_2000_cfg1 | singleton_neither | 17 | 2 |
| reference_empirical_2000_cfg1 | singleton_new_only | 2 | 0 |
| aligned_teacher_empirical_0_cfg1 | singleton_both | 31 | 22 |
| aligned_teacher_empirical_0_cfg1 | singleton_fixed_only | 1 | 0 |
| aligned_teacher_empirical_0_cfg1 | singleton_neither | 17 | 5 |
| aligned_teacher_empirical_0_cfg1 | singleton_new_only | 2 | 0 |
| aligned_teacher_empirical_2000_cfg1 | singleton_both | 31 | 11 |
| aligned_teacher_empirical_2000_cfg1 | singleton_fixed_only | 1 | 0 |
| aligned_teacher_empirical_2000_cfg1 | singleton_neither | 17 | 4 |
| aligned_teacher_empirical_2000_cfg1 | singleton_new_only | 2 | 0 |
| pca_teacher_empirical_0_cfg1 | singleton_both | 31 | 22 |
| pca_teacher_empirical_0_cfg1 | singleton_fixed_only | 1 | 0 |
| pca_teacher_empirical_0_cfg1 | singleton_neither | 17 | 5 |
| pca_teacher_empirical_0_cfg1 | singleton_new_only | 2 | 0 |
| pca_teacher_empirical_2000_cfg1 | singleton_both | 31 | 14 |
| pca_teacher_empirical_2000_cfg1 | singleton_fixed_only | 1 | 0 |
| pca_teacher_empirical_2000_cfg1 | singleton_neither | 17 | 7 |
| pca_teacher_empirical_2000_cfg1 | singleton_new_only | 2 | 0 |
