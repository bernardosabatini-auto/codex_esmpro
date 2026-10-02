# Matched teacher-prior and frame comparison

Checkpoint: 500. Initialization, target order, learning-rate schedule, configurations and within-prior label draws verified. Both balanced arms use the same frozen protocol.

Training-only teacher states. Paired family intervals are unadjusted; intermediate results are provisional. Singleton recall is averaged over proteins containing a singleton state. Equal-state sampling changes the target prior; both frequency comparisons remain visible.

| Arm / prior / CFG | Recall @2A | Recall @1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV | Singleton recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| reference_empirical_cfg1 | 0.42321 | 0.29048 | 0.99512 | 0.94358 | 0.45898 | 0.61747 | 0.21000 |
| aligned_teacher_empirical_cfg1 | 0.67932 | 0.55015 | 0.99219 | 0.96479 | 0.17773 | 0.50552 | 0.34000 |
| pca_teacher_empirical_cfg1 | 0.61310 | 0.52723 | 0.99805 | 0.96995 | 0.18555 | 0.53176 | 0.27333 |
| aligned_teacher_balanced_cfg1 | 0.89881 | 0.81443 | 0.99609 | 0.96415 | 0.26367 | 0.36192 | 0.75000 |
| pca_teacher_balanced_cfg1 | 0.87589 | 0.77753 | 0.99902 | 0.96717 | 0.35059 | 0.38732 | 0.80000 |
| reference_empirical_cfg2 | 0.41429 | 0.29226 | 0.98047 | 0.89669 | 0.48828 | 0.62934 | 0.17667 |
| aligned_teacher_empirical_cfg2 | 0.55446 | 0.47827 | 0.98828 | 0.93506 | 0.22852 | 0.56502 | 0.26333 |
| pca_teacher_empirical_cfg2 | 0.49062 | 0.44182 | 0.98828 | 0.92745 | 0.24121 | 0.59705 | 0.11667 |
| aligned_teacher_balanced_cfg2 | 0.72426 | 0.59539 | 0.98438 | 0.93073 | 0.34961 | 0.49041 | 0.57000 |
| pca_teacher_balanced_cfg2 | 0.68199 | 0.57515 | 0.98828 | 0.92622 | 0.38477 | 0.51835 | 0.48000 |

| Primary CFG1 comparison | Recall difference | Paired 95% interval | Validity difference |
|---|---:|---|---:|
| aligned_teacher_balanced_cfg1_vs_initial | +0.15134 | [0.06696428571428571, 0.23467261904761905] | +0.00391 |
| aligned_teacher_balanced_cfg1_vs_reference | +0.47560 | [0.4052046130952381, 0.5479166666666667] | +0.00098 |
| aligned_teacher_balanced_cfg1_vs_empirical_same_frame | +0.21949 | [0.1441964285714286, 0.2952455357142857] | +0.00391 |
| aligned_teacher_balanced_cfg1_vs_pca_same_prior | +0.02292 | [-0.03958333333333334, 0.08645833333333333] | -0.00293 |
| pca_teacher_balanced_cfg1_vs_initial | +0.12842 | [0.020089285714285712, 0.23229538690476187] | +0.00684 |
| pca_teacher_balanced_cfg1_vs_reference | +0.45268 | [0.36696428571428574, 0.5367559523809524] | +0.00391 |
| pca_teacher_balanced_cfg1_vs_empirical_same_frame | +0.26280 | [0.1836309523809524, 0.3447916666666667] | +0.00098 |

aligned_teacher original capacity screen: PASS; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': True, 'validity_margin': True}.

pca_teacher original capacity screen: PASS; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': True, 'validity_margin': True}.

No result here establishes biological populations, unseen-family performance, or a faster deployable model.
