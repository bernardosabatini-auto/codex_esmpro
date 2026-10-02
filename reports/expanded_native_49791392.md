# Restricted adaptation: separate accuracy transfer

Status: complete; checkpoint 2000.

64 separate tuning families, three paired samples. Full-network and restricted-tail balanced training at both seeds, CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_full_cfg1 | 0.79902 | +0.01518 | [0.011461015431395462, 0.018966480433890008] | 0.96354 | -0.01562 | False |
| seed2026100171_tail_cfg1 | 0.76908 | -0.01475 | [-0.02237174631060939, -0.008049930925118468] | 0.94271 | -0.03646 | False |
| seed2026100181_full_cfg1 | 0.79889 | +0.01505 | [0.011282528446824789, 0.01901880906765806] | 0.96875 | -0.01042 | False |
| seed2026100181_tail_cfg1 | 0.76892 | -0.01492 | [-0.02276037017094747, -0.007862024536579092] | 0.93229 | -0.04688 | False |

Seed2026100171, tail minus full: CA-lDDT -0.02993,95% interval [-0.037162634966735504, -0.023269868152512415]; validity -0.02083.

Seed2026100181, tail minus full: CA-lDDT -0.02996,95% interval [-0.03753938224435865, -0.023241748410136008]; validity -0.03646.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
