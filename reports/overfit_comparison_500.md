# Matched small-ensemble learning comparison

Checkpoint: 500. Same initialization, labels, target batches and random label draws verified. Teacher arms differ only in coordinate frame.

Teacher-defined training states only; no biological-state or generalization claim. CFG settings and both contact thresholds remain visible.

| Arm / guidance | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV |
|---|---:|---:|---:|---:|---:|---:|
| reference_cfg1 | 0.42321 | 0.29048 | 0.99512 | 0.94358 | 0.97364 | 0.45898 |
| aligned_teacher_cfg1 | 0.67932 | 0.55015 | 0.99219 | 0.96479 | 0.93113 | 0.17773 |
| pca_teacher_cfg1 | 0.61310 | 0.52723 | 0.99805 | 0.96995 | 0.93537 | 0.18555 |
| reference_cfg2 | 0.41429 | 0.29226 | 0.98047 | 0.89669 | 0.92503 | 0.48828 |
| aligned_teacher_cfg2 | 0.55446 | 0.47827 | 0.98828 | 0.93506 | 0.90010 | 0.22852 |
| pca_teacher_cfg2 | 0.49062 | 0.44182 | 0.98828 | 0.92745 | 0.89365 | 0.24121 |

Paired 95% intervals below resample frozen sequence families and are unadjusted for multiple comparisons. Positive differences favor the named candidate.

| Candidate / comparator / CFG | Recall difference | 95% interval | Validity difference | 95% interval |
|---|---:|---|---:|---|
| aligned_teacher / initial / 1 | -0.06815 | [-0.153125, 0.013701636904761741] | +0.00000 | [-0.0068359375, 0.0068359375] |
| aligned_teacher / reference / 1 | +0.25610 | [0.16875, 0.3366071428571429] | -0.00293 | [-0.0087890625, 0.0009765625] |
| pca_teacher / initial / 1 | -0.13438 | [-0.22931919642857143, -0.04196428571428572] | +0.00586 | [0.0, 0.013671875] |
| pca_teacher / reference / 1 | +0.18988 | [0.09062500000000001, 0.28288690476190476] | +0.00293 | [0.0, 0.0087890625] |

Aligned minus PCA recall at CFG1: +0.06622, paired 95% interval [0.010416666666666666, 0.13392857142857142].

aligned_teacher capacity screen: NOT PASSED; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': False, 'validity_margin': True}.

pca_teacher capacity screen: NOT PASSED; {'recall_gain': True, 'positive_ci_vs_reference': True, 'positive_ci_vs_initial': False, 'validity_margin': True}.

A screen at an intermediate checkpoint is provisional. Even a final training-capacity pass requires separate development/generalization testing and does not authorize a model-quality claim.
