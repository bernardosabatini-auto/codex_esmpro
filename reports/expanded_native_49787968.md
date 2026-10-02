# Restricted adaptation: separate accuracy transfer

Status: complete; checkpoint 500.

64 separate tuning families, three paired samples. Full-network and restricted-tail balanced training at both seeds, CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_full_cfg1 | 0.78794 | +0.00410 | [-0.001569854335074207, 0.00901624221794908] | 0.95312 | -0.02604 | False |
| seed2026100171_tail_cfg1 | 0.76500 | -0.01884 | [-0.026413357803593693, -0.011961305953964248] | 0.92708 | -0.05208 | False |
| seed2026100181_full_cfg1 | 0.78827 | +0.00443 | [-0.001620546576334707, 0.009320844237129722] | 0.96354 | -0.01562 | False |
| seed2026100181_tail_cfg1 | 0.76286 | -0.02097 | [-0.029257480696571143, -0.013390198245186093] | 0.93229 | -0.04688 | False |

Seed2026100171, tail minus full: CA-lDDT -0.02294,95% interval [-0.028707432922753105, -0.01776030971114926]; validity -0.02604.

Seed2026100181, tail minus full: CA-lDDT -0.02541,95% interval [-0.03287241335172704, -0.018665657287151804]; validity -0.03125.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
