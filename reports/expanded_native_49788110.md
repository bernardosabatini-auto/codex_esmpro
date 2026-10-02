# Fixed checkpoint interpolation: separate accuracy transfer

Status: complete; checkpoint 2000.

64 separate tuning families, three paired samples. Full balanced2000 and fixed50/50 blends with initialization at both seeds, CFG1 versus originalCFG2. Euler25/decoder3, strict FP32. All samples retained. Blended weights do not inherit the source model training-capacity qualification. No independent-test scoring; unadjusted family intervals.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_full_cfg1 | 0.79902 | +0.01518 | [0.011461015431395462, 0.018966480433890008] | 0.96354 | -0.01562 | False |
| seed2026100171_blend_cfg1 | 0.79034 | +0.00651 | [0.0029548092890616497, 0.009838341510697493] | 0.96354 | -0.01562 | False |
| seed2026100181_full_cfg1 | 0.79889 | +0.01505 | [0.011282528446824789, 0.01901880906765806] | 0.96875 | -0.01042 | False |
| seed2026100181_blend_cfg1 | 0.79036 | +0.00652 | [0.0023909265896398385, 0.010398308539288748] | 0.96875 | -0.01042 | False |

Seed2026100171, blend minus full: CA-lDDT -0.00867,95% interval [-0.012181642268511813, -0.0055364585070917195]; validity +0.00000.

Seed2026100181, blend minus full: CA-lDDT -0.00853,95% interval [-0.012499737802140747, -0.004913700818958733]; validity -0.00000.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
