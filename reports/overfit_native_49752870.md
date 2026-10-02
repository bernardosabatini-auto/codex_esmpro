# Accuracy transfer from32-protein capacity training

Status: complete.

All four matched2000-update teacher checkpoints and the original model;64 separate tuning families,three paired seeds,CFG1/2,Euler25,decoder3,strict FP32. References are AFDB predictions. No locked-test scoring. All settings and geometry failures remain included. Family intervals are unadjusted. This measures transfer from a small training panel, not independent-test performance or biological populations.

| Head / CFG | CA-lDDT | Delta versus original CFG2 | 95% interval | Valid | Validity delta | Quality gate |
|---|---:|---:|---|---:|---:|---|
| original_cfg1 | 0.77354 | -0.01030 | [-0.015215626592707223, -0.005594808140782568] | 0.97396 | -0.00521 | False |
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| aligned_teacher_empirical_cfg1 | 0.79343 | +0.00959 | [0.004909058377705342, 0.014042063264061492] | 0.95833 | -0.02083 | False |
| aligned_teacher_empirical_cfg2 | 0.77569 | -0.00814 | [-0.013947877428865671, -0.001969966673566506] | 0.96875 | -0.01042 | False |
| pca_teacher_empirical_cfg1 | 0.79429 | +0.01045 | [0.005915836878011058, 0.015058537543030883] | 0.96875 | -0.01042 | False |
| pca_teacher_empirical_cfg2 | 0.77086 | -0.01298 | [-0.018945545430384226, -0.0062944127437805555] | 0.96354 | -0.01562 | False |
| aligned_teacher_balanced_cfg1 | 0.79536 | +0.01153 | [0.007166810177097332, 0.015830215812880015] | 0.98438 | +0.00521 | True |
| aligned_teacher_balanced_cfg2 | 0.77672 | -0.00712 | [-0.013399430688710494, -0.0004008895583648398] | 0.96354 | -0.01562 | False |
| pca_teacher_balanced_cfg1 | 0.79555 | +0.01172 | [0.007688912887104716, 0.01580709703722308] | 0.96875 | -0.01042 | False |
| pca_teacher_balanced_cfg2 | 0.77011 | -0.01372 | [-0.019948768190239656, -0.006737705893890766] | 0.96354 | -0.01562 | False |

| Balanced minus empirical at matched frame/CFG | CA-lDDT difference | 95% interval | Validity difference |
|---|---:|---|---:|
| aligned_teacher_cfg1 | +0.00193 | [-0.00029508796132415296, 0.00427044358475552] | +0.02604 |
| aligned_teacher_cfg2 | +0.00102 | [-0.001257550331139382, 0.0034474954068081033] | -0.00521 |
| pca_teacher_cfg1 | +0.00127 | [-0.0002924783947069892, 0.0031378813685631083] | +0.00000 |
| pca_teacher_cfg2 | -0.00074 | [-0.003040883507248726, 0.0015874581129428453] | -0.00000 |

Training-capacity gains do not imply generalization. A qualified model still needs separate ensemble development assessment and training-seed replication before promotion. All scheduled endpoints retain their original budgets.
