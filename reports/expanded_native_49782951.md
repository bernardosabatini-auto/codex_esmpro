# Replicated122-family training: separate accuracy transfer

Status: complete; checkpoint 2000.

64 separate tuning families, three paired samples. Both priors and optimization seeds retained at CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_empirical_cfg1 | 0.79751 | +0.01367 | [0.010160225728193818, 0.017359398083339098] | 0.96875 | -0.01042 | False |
| seed2026100171_balanced_cfg1 | 0.79902 | +0.01518 | [0.011461015431395462, 0.018966480433890008] | 0.96354 | -0.01562 | False |
| seed2026100181_empirical_cfg1 | 0.79395 | +0.01011 | [0.0034553408276768883, 0.015248528156296784] | 0.93750 | -0.04167 | False |
| seed2026100181_balanced_cfg1 | 0.79889 | +0.01505 | [0.011282528446824789, 0.01901880906765806] | 0.96875 | -0.01042 | False |

Seed2026100171, balanced minus empirical: CA-lDDT +0.00151,95% interval [-0.0005781835976887334, 0.003723721071627752]; validity -0.00521.

Seed2026100181, balanced minus empirical: CA-lDDT +0.00494,95% interval [0.0008534356629423629, 0.010719059201855716]; validity +0.03125.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
