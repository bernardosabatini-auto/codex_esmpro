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
