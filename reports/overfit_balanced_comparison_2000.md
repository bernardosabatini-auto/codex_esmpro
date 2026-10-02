# Matched teacher-prior and frame comparison

Checkpoint: 2000. Initialization, target order, learning-rate schedule, configurations and within-prior label draws verified. Both balanced arms use the same frozen protocol.

Training-only teacher states. Paired family intervals are unadjusted; intermediate results are provisional. Singleton recall is averaged over proteins containing a singleton state. Equal-state sampling changes the target prior; both frequency comparisons remain visible.

| Arm / prior / CFG | Recall @2A | Recall @1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV | Singleton recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| reference_empirical_cfg1 | 0.37262 | 0.26667 | 0.99902 | 0.94764 | 0.47949 | 0.64895 | 0.15000 |
| aligned_teacher_empirical_cfg1 | 0.62500 | 0.58170 | 0.99902 | 0.98183 | 0.15137 | 0.50945 | 0.24333 |
| pca_teacher_empirical_cfg1 | 0.66369 | 0.59970 | 0.99902 | 0.98241 | 0.16016 | 0.52196 | 0.33000 |
| aligned_teacher_balanced_cfg1 | 0.89360 | 0.84509 | 0.99805 | 0.98035 | 0.29980 | 0.30724 | 0.84000 |
| pca_teacher_balanced_cfg1 | 0.85610 | 0.81726 | 0.99902 | 0.98315 | 0.37793 | 0.33956 | 0.80000 |
| reference_empirical_cfg2 | 0.36190 | 0.27187 | 0.93848 | 0.89068 | 0.53223 | 0.68219 | 0.13000 |
| aligned_teacher_empirical_cfg2 | 0.45238 | 0.42024 | 0.98047 | 0.94617 | 0.23438 | 0.58959 | 0.08667 |
| pca_teacher_empirical_cfg2 | 0.48571 | 0.47054 | 0.97461 | 0.92794 | 0.22559 | 0.56997 | 0.17000 |
| aligned_teacher_balanced_cfg2 | 0.72738 | 0.65149 | 0.97754 | 0.94451 | 0.34766 | 0.45886 | 0.58667 |
| pca_teacher_balanced_cfg2 | 0.70134 | 0.66295 | 0.98242 | 0.92663 | 0.39355 | 0.47528 | 0.60000 |

| Primary CFG1 comparison | Recall difference | Paired 95% interval | Validity difference |
|---|---:|---|---:|
| aligned_teacher_balanced_cfg1_vs_initial | +0.14613 | [0.04404761904761905, 0.24479910714285705] | +0.00586 |
| aligned_teacher_balanced_cfg1_vs_reference | +0.52098 | [0.42603794642857146, 0.6038690476190476] | -0.00098 |
| aligned_teacher_balanced_cfg1_vs_empirical_same_frame | +0.26860 | [0.18333333333333335, 0.3549107142857143] | -0.00098 |
| aligned_teacher_balanced_cfg1_vs_pca_same_prior | +0.03750 | [-0.01636904761904763, 0.09970238095238096] | -0.00098 |
| pca_teacher_balanced_cfg1_vs_initial | +0.10863 | [-0.0007514880952380994, 0.2107142857142857] | +0.00684 |
| pca_teacher_balanced_cfg1_vs_reference | +0.48348 | [0.37976190476190474, 0.5760453869047617] | +0.00000 |
| pca_teacher_balanced_cfg1_vs_empirical_same_frame | +0.19241 | [0.09345238095238095, 0.2885416666666667] | +0.00000 |

aligned_teacher original capacity screen: PASS; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': True, 'validity_margin': True}.

pca_teacher original capacity screen: NOT PASSED; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': False, 'validity_margin': True}.

No result here establishes biological populations, unseen-family performance, or a faster deployable model.
