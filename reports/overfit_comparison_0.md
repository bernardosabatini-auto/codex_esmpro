# Matched small-ensemble learning comparison

Checkpoint: 0. Same initialization, labels, target batches and random label draws verified. Teacher arms differ only in coordinate frame.

Teacher-defined training states only; no biological-state or generalization claim. CFG settings and both contact thresholds remain visible.

| Arm / guidance | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV |
|---|---:|---:|---:|---:|---:|---:|
| reference_cfg1 | 0.74747 | 0.50446 | 0.99219 | 0.89841 | 0.88265 | 0.51074 |
| aligned_teacher_cfg1 | 0.74747 | 0.50446 | 0.99219 | 0.89841 | 0.88265 | 0.51074 |
| pca_teacher_cfg1 | 0.74747 | 0.50446 | 0.99219 | 0.89841 | 0.88265 | 0.51074 |
| reference_cfg2 | 0.56741 | 0.35729 | 0.99121 | 0.89422 | 0.88048 | 0.53223 |
| aligned_teacher_cfg2 | 0.56741 | 0.35729 | 0.99121 | 0.89422 | 0.88048 | 0.53223 |
| pca_teacher_cfg2 | 0.56741 | 0.35729 | 0.99121 | 0.89422 | 0.88048 | 0.53223 |

Paired 95% intervals below resample frozen sequence families and are unadjusted for multiple comparisons. Positive differences favor the named candidate.

| Candidate / comparator / CFG | Recall difference | 95% interval | Validity difference | 95% interval |
|---|---:|---|---:|---|
| aligned_teacher / initial / 1 | +0.00000 | [0.0, 0.0] | +0.00000 | [0.0, 0.0] |
| aligned_teacher / reference / 1 | +0.00000 | [0.0, 0.0] | +0.00000 | [0.0, 0.0] |
| pca_teacher / initial / 1 | +0.00000 | [0.0, 0.0] | +0.00000 | [0.0, 0.0] |
| pca_teacher / reference / 1 | +0.00000 | [0.0, 0.0] | +0.00000 | [0.0, 0.0] |

Aligned minus PCA recall at CFG1: +0.00000, paired 95% interval [0.0, 0.0].

aligned_teacher capacity screen: NOT PASSED; {'recall_gain': False, 'positive_ci_vs_reference': False, 'positive_ci_vs_initial': False, 'validity_margin': True}.

pca_teacher capacity screen: NOT PASSED; {'recall_gain': False, 'positive_ci_vs_reference': False, 'positive_ci_vs_initial': False, 'validity_margin': True}.

A screen at an intermediate checkpoint is provisional. Even a final training-capacity pass requires separate development/generalization testing and does not authorize a model-quality claim.
