# Matched small-ensemble learning comparison

Checkpoint: 2000. Same initialization, labels, target batches and random label draws verified. Teacher arms differ only in coordinate frame.

Teacher-defined training states only; no biological-state or generalization claim. CFG settings and both contact thresholds remain visible.

| Arm / guidance | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV |
|---|---:|---:|---:|---:|---:|---:|
| reference_cfg1 | 0.37262 | 0.26667 | 0.99902 | 0.94764 | 0.99070 | 0.47949 |
| aligned_teacher_cfg1 | 0.62500 | 0.58170 | 0.99902 | 0.98183 | 0.94361 | 0.15137 |
| pca_teacher_cfg1 | 0.66369 | 0.59970 | 0.99902 | 0.98241 | 0.94397 | 0.16016 |
| reference_cfg2 | 0.36190 | 0.27187 | 0.93848 | 0.89068 | 0.92867 | 0.53223 |
| aligned_teacher_cfg2 | 0.45238 | 0.42024 | 0.98047 | 0.94617 | 0.90876 | 0.23438 |
| pca_teacher_cfg2 | 0.48571 | 0.47054 | 0.97461 | 0.92794 | 0.89120 | 0.22559 |

Paired 95% intervals below resample frozen sequence families and are unadjusted for multiple comparisons. Positive differences favor the named candidate.

| Candidate / comparator / CFG | Recall difference | 95% interval | Validity difference | 95% interval |
|---|---:|---|---:|---|
| aligned_teacher / initial / 1 | -0.12247 | [-0.22291666666666668, -0.018750000000000006] | +0.00684 | [0.0009765625, 0.0146484375] |
| aligned_teacher / reference / 1 | +0.25238 | [0.1575892857142857, 0.34479910714285705] | +0.00000 | [-0.0029296875, 0.0029296875] |
| pca_teacher / initial / 1 | -0.08378 | [-0.19270833333333337, 0.0251488095238095] | +0.00684 | [0.0009765625, 0.0146484375] |
| pca_teacher / reference / 1 | +0.29107 | [0.1982105654761905, 0.3788727678571428] | +0.00000 | [-0.0029296875, 0.0029296875] |

Aligned minus PCA recall at CFG1: -0.03869, paired 95% interval [-0.10595238095238095, 0.03333333333333334].

aligned_teacher capacity screen: NOT PASSED; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': False, 'validity_margin': True}.

pca_teacher capacity screen: NOT PASSED; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': False, 'validity_margin': True}.

A screen at an intermediate checkpoint is provisional. Even a final training-capacity pass requires separate development/generalization testing and does not authorize a model-quality claim.
