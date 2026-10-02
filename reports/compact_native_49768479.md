# Compact conditioning: full tuning-panel validation

Status: complete.

64 tuning families, three paired samples, two frozen checkpoints, expanded/compact strict FP32. Every expanded output is compared with its frozen source; every compact output with its same-device expanded counterpart. All768 scores and768 agreement controls plus16 batching controls required. Unadjusted family intervals; invalid samples retained. No locked tests or end-to-end speed claim.

| Pipeline | CA-lDDT | Delta vs fresh original |95% interval | Valid | Validity delta | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_fp32 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| original_compact | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| aligned_teacher_balanced_fp32 | 0.79427 | +0.01043 | [0.005419140677357357, 0.015176399083433979] | 0.97396 | -0.00521 | True |
| aligned_teacher_balanced_compact | 0.79427 | +0.01043 | [0.005419140677357357, 0.015176399083433979] | 0.97396 | -0.00521 | True |

original, compact minus expanded: CA-lDDT +0.000000,95% interval [0.0, 0.0]; validity +0.000000; noninferior True.

aligned_teacher_balanced, compact minus expanded: CA-lDDT +0.000000,95% interval [0.0, 0.0]; validity +0.000000; noninferior True.

Maximum frozen-output RMSD 0.029013A; implementation RMSD 0.000000A. Qualified heads: ['original', 'aligned_teacher_balanced'].
Passing permits separate48-family ensemble assessment and matched resident sequence timing, not automatic adoption.
