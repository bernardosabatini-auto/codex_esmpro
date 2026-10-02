# Scoped TF32x3 numerical and stage-speed probe

Status: complete; qualifies for broader validation: False.

Four longest tuning-bucket proteins, original CFG2 and balanced500 CFG1, Euler25/decoder3. Only DiT MLP and QKV/output projections change arithmetic. This is not IEEE equality, full-panel accuracy, or an end-to-end speed measurement. All micro and structural controls must pass before follow-up.

Worst paired CA-RMSD: 0.002222 A; minimum pair CA-lDDT: 1.000000. Maximum TF32x3 micro relative-RMS error: 1.45e-07.
Batch32 ratio of summed per-target median times: 0.9834. Warmup totals (including first compilation): {'fp32': 89.0322885774076, 'tf32x3': 93.54658800223842}. Peak reserved: 42.07 GiB.

| Head | Target | Layout | FP32 seconds | TF32x3 seconds | Speed ratio |
|---|---|---|---:|---:|---:|
| original | AF-A0A1H4C073-F1-model_v6 | single_exact | 0.3521 | 0.5213 | 0.676 |
| original | AF-A0A1H4C073-F1-model_v6 | single_padded | 0.3519 | 0.5207 | 0.676 |
| original | AF-A0A1H4C073-F1-model_v6 | batch8 | 0.9819 | 1.0012 | 0.981 |
| original | AF-A0A1H4C073-F1-model_v6 | batch32 | 3.1140 | 3.1068 | 1.002 |
| original | AF-H0T4D4-F1-model_v6 | single_exact | 0.4935 | 0.6295 | 0.784 |
| original | AF-H0T4D4-F1-model_v6 | single_padded | 0.4832 | 0.6325 | 0.764 |
| original | AF-H0T4D4-F1-model_v6 | batch8 | 1.8573 | 1.8358 | 1.012 |
| original | AF-H0T4D4-F1-model_v6 | batch32 | 7.4088 | 7.3672 | 1.006 |
| original | AF-A0A562IH95-F1-model_v6 | single_exact | 0.7221 | 0.8191 | 0.882 |
| original | AF-A0A562IH95-F1-model_v6 | single_padded | 0.7260 | 0.8259 | 0.879 |
| original | AF-A0A562IH95-F1-model_v6 | batch8 | 3.3125 | 3.2953 | 1.005 |
| original | AF-A0A562IH95-F1-model_v6 | batch32 | 12.7802 | 12.8806 | 0.992 |
| original | AF-A0A2G5UFT3-F1-model_v6 | single_exact | 0.9915 | 1.0505 | 0.944 |
| original | AF-A0A2G5UFT3-F1-model_v6 | single_padded | 0.9749 | 1.0440 | 0.934 |
| original | AF-A0A2G5UFT3-F1-model_v6 | batch8 | 4.8849 | 4.8599 | 1.005 |
| original | AF-A0A2G5UFT3-F1-model_v6 | batch32 | 18.3441 | 19.0195 | 0.964 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | single_exact | 0.1970 | 0.2758 | 0.714 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | single_padded | 0.1972 | 0.2758 | 0.715 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | batch8 | 0.5148 | 0.5302 | 0.971 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | batch32 | 1.6709 | 1.6574 | 1.008 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | single_exact | 0.2700 | 0.3399 | 0.794 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | single_padded | 0.2653 | 0.3407 | 0.779 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | batch8 | 0.9972 | 0.9879 | 1.009 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | batch32 | 3.9445 | 3.9091 | 1.009 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | single_exact | 0.4081 | 0.4550 | 0.897 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | single_padded | 0.4093 | 0.4604 | 0.889 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | batch8 | 1.7941 | 1.7850 | 1.005 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | batch32 | 6.8254 | 6.8571 | 0.995 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | single_exact | 0.5732 | 0.6017 | 0.953 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | single_padded | 0.5639 | 0.5986 | 0.942 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | batch8 | 2.6618 | 2.6463 | 1.006 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | batch32 | 9.8779 | 10.2449 | 0.964 |

Failed structural controls: []
