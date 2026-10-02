# Replicated122-family training: separate accuracy transfer

Status: complete; checkpoint 500.

64 separate tuning families, three paired samples. Both priors and optimization seeds retained at CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_empirical_cfg1 | 0.79288 | +0.00904 | [0.0051314770177791815, 0.01319946506437796] | 0.96354 | -0.01562 | False |
| seed2026100171_balanced_cfg1 | 0.78794 | +0.00410 | [-0.001569854335074207, 0.00901624221794908] | 0.95312 | -0.02604 | False |
| seed2026100181_empirical_cfg1 | 0.78693 | +0.00309 | [-0.004399154761459621, 0.009143243047777808] | 0.95833 | -0.02083 | False |
| seed2026100181_balanced_cfg1 | 0.78827 | +0.00443 | [-0.001620546576334707, 0.009320844237129722] | 0.96354 | -0.01562 | False |

Seed2026100171, balanced minus empirical: CA-lDDT -0.00494,95% interval [-0.009809209822503905, -0.0014461151051941056]; validity -0.01042.

Seed2026100181, balanced minus empirical: CA-lDDT +0.00135,95% interval [-0.0016046011513630677, 0.005775902534137011]; validity +0.00521.

Both balanced seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
