# Compact single-sequence conditioning probe

Status: complete; qualifies for broader validation: True.

Original CFG2 and balanced500 CFG1, four longest tuning-bucket proteins, exact/padded single and batches8/32. Both paths retain strict FP32. Three measured repeats after one warmup per layout; allocator cache cleared between layouts. Flow, decoder and output transfer included, ESMC excluded. All80 structural controls required. This is not full-panel accuracy or an end-to-end speedup.

Worst CA-RMSD 0.002023A; minimum pair CA-lDDT 1.000000. Batch32 ratio of summed medians 1.0970.

| Head | Target | Layout | Expanded seconds | Compact seconds | Speed ratio | Expanded allocated GiB | Compact allocated GiB |
|---|---|---|---:|---:|---:|---:|---:|
| original | AF-A0A1H4C073-F1-model_v6 | single_exact | 0.3501 | 0.3468 | 1.010 | 1.92 | 1.92 |
| original | AF-A0A1H4C073-F1-model_v6 | single_padded | 0.3484 | 0.3477 | 1.002 | 1.92 | 1.92 |
| original | AF-A0A1H4C073-F1-model_v6 | batch8 | 0.9842 | 0.9747 | 1.010 | 2.45 | 2.45 |
| original | AF-A0A1H4C073-F1-model_v6 | batch32 | 3.1234 | 3.0344 | 1.029 | 4.39 | 4.39 |
| original | AF-H0T4D4-F1-model_v6 | single_exact | 0.4883 | 0.4815 | 1.014 | 2.24 | 2.24 |
| original | AF-H0T4D4-F1-model_v6 | single_padded | 0.4778 | 0.4777 | 1.000 | 2.25 | 2.25 |
| original | AF-H0T4D4-F1-model_v6 | batch8 | 1.8638 | 1.7848 | 1.044 | 4.33 | 4.33 |
| original | AF-H0T4D4-F1-model_v6 | batch32 | 7.4100 | 6.9040 | 1.073 | 11.90 | 11.90 |
| original | AF-A0A562IH95-F1-model_v6 | single_exact | 0.7219 | 0.7218 | 1.000 | 2.78 | 2.78 |
| original | AF-A0A562IH95-F1-model_v6 | single_padded | 0.7230 | 0.7212 | 1.002 | 2.80 | 2.80 |
| original | AF-A0A562IH95-F1-model_v6 | batch8 | 3.3250 | 3.0033 | 1.107 | 7.47 | 7.47 |
| original | AF-A0A562IH95-F1-model_v6 | batch32 | 12.7921 | 11.6783 | 1.095 | 24.45 | 24.45 |
| original | AF-A0A2G5UFT3-F1-model_v6 | single_exact | 0.9908 | 0.9863 | 1.005 | 3.56 | 3.56 |
| original | AF-A0A2G5UFT3-F1-model_v6 | single_padded | 0.9762 | 0.9747 | 1.002 | 3.57 | 3.57 |
| original | AF-A0A2G5UFT3-F1-model_v6 | batch8 | 4.8976 | 4.4199 | 1.108 | 11.86 | 11.86 |
| original | AF-A0A2G5UFT3-F1-model_v6 | batch32 | 18.3713 | 16.3262 | 1.125 | 42.01 | 42.01 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | single_exact | 0.2005 | 0.1973 | 1.016 | 1.92 | 1.92 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | single_padded | 0.2009 | 0.1978 | 1.016 | 1.92 | 1.92 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | batch8 | 0.5151 | 0.5072 | 1.016 | 2.45 | 2.45 |
| aligned_teacher_balanced | AF-A0A1H4C073-F1-model_v6 | batch32 | 1.6671 | 1.6207 | 1.029 | 4.39 | 4.39 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | single_exact | 0.2655 | 0.2652 | 1.001 | 2.24 | 2.24 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | single_padded | 0.2665 | 0.2656 | 1.004 | 2.25 | 2.25 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | batch8 | 0.9936 | 0.9545 | 1.041 | 4.33 | 4.33 |
| aligned_teacher_balanced | AF-H0T4D4-F1-model_v6 | batch32 | 3.9408 | 3.6780 | 1.071 | 11.90 | 11.90 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | single_exact | 0.4071 | 0.4046 | 1.006 | 2.78 | 2.78 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | single_padded | 0.4088 | 0.4080 | 1.002 | 2.80 | 2.80 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | batch8 | 1.7894 | 1.6400 | 1.091 | 7.47 | 7.47 |
| aligned_teacher_balanced | AF-A0A562IH95-F1-model_v6 | batch32 | 6.8297 | 6.2589 | 1.091 | 24.45 | 24.45 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | single_exact | 0.5683 | 0.5695 | 0.998 | 3.56 | 3.56 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | single_padded | 0.5640 | 0.5637 | 1.000 | 3.57 | 3.57 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | batch8 | 2.6589 | 2.4242 | 1.097 | 11.86 | 11.86 |
| aligned_teacher_balanced | AF-A0A2G5UFT3-F1-model_v6 | batch32 | 9.8841 | 8.8584 | 1.116 | 42.01 | 42.01 |

Failed controls: []
