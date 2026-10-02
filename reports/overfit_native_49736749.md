# Accuracy transfer from32-protein capacity training

Status: complete.

All four matched500-update teacher checkpoints and the original model;64 separate tuning families,three paired seeds,CFG1/2,Euler25,decoder3,strict FP32. References are AFDB predictions. No locked-test scoring. All settings and geometry failures remain included. Family intervals are unadjusted. This measures transfer from a small training panel, not independent-test performance or biological populations.

| Head / CFG | CA-lDDT | Delta versus original CFG2 | 95% interval | Valid | Validity delta | Quality gate |
|---|---:|---:|---|---:|---:|---|
| original_cfg1 | 0.77354 | -0.01030 | [-0.015215626592707223, -0.005594808140782568] | 0.97396 | -0.00521 | False |
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| aligned_teacher_empirical_cfg1 | 0.78746 | +0.00362 | [-0.005146841973882167, 0.010969530007588229] | 0.95833 | -0.02083 | False |
| aligned_teacher_empirical_cfg2 | 0.77956 | -0.00428 | [-0.008673699835389724, 0.0003256380217812925] | 0.95833 | -0.02083 | False |
| pca_teacher_empirical_cfg1 | 0.79489 | +0.01105 | [0.007056137665299615, 0.014996500518134673] | 0.97396 | -0.00521 | True |
| pca_teacher_empirical_cfg2 | 0.77715 | -0.00669 | [-0.01196578645969252, -0.0012963896235747533] | 0.96354 | -0.01562 | False |
| aligned_teacher_balanced_cfg1 | 0.79427 | +0.01043 | [0.005421782850849982, 0.01518006759196506] | 0.97396 | -0.00521 | True |
| aligned_teacher_balanced_cfg2 | 0.77918 | -0.00466 | [-0.009586837071167621, 0.0007117852280629297] | 0.96875 | -0.01042 | False |
| pca_teacher_balanced_cfg1 | 0.79363 | +0.00979 | [0.005857451980265059, 0.013791165816725088] | 0.96875 | -0.01042 | False |
| pca_teacher_balanced_cfg2 | 0.77594 | -0.00790 | [-0.012767194339985256, -0.0026081002394728508] | 0.95312 | -0.02604 | False |

| Balanced minus empirical at matched frame/CFG | CA-lDDT difference | 95% interval | Validity difference |
|---|---:|---|---:|
| aligned_teacher_cfg1 | +0.00681 | [0.0013451161467383438, 0.01410102091215884] | +0.01562 |
| aligned_teacher_cfg2 | -0.00038 | [-0.003075414286142702, 0.002514020370602509] | +0.01042 |
| pca_teacher_cfg1 | -0.00126 | [-0.0031165744716656553, 0.0005421108234864322] | -0.00521 |
| pca_teacher_cfg2 | -0.00121 | [-0.0030964448160231105, 0.0007074982292449388] | -0.01042 |

Training-capacity gains do not imply generalization. A qualified model still needs separate ensemble development assessment and training-seed replication before promotion. Both scheduled2000-update endpoints retain their original budgets.
