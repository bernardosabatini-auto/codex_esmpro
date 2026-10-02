# Direct decoded geometry training: separate accuracy transfer

Status: complete; checkpoint 2000.

64 separate tuning families, three paired samples. Full balanced122 controls and direct decoded-geometry training at both seeds, CFG1 versus originalCFG2. Euler25/decoder3, strict FP32, all samples retained. No output repair or independent-test scoring. Unadjusted family intervals.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_full_cfg1 | 0.79902 | +0.01518 | [0.011461015431395462, 0.018966480433890008] | 0.96354 | -0.01562 | False |
| seed2026100171_geometry_cfg1 | 0.79885 | +0.01501 | [0.010962801072035462, 0.01919530494337829] | 0.95833 | -0.02083 | False |
| seed2026100181_full_cfg1 | 0.79889 | +0.01505 | [0.011282528446824789, 0.01901880906765806] | 0.96875 | -0.01042 | False |
| seed2026100181_geometry_cfg1 | 0.79955 | +0.01571 | [0.011848196294910962, 0.019723398266622307] | 0.97396 | -0.00521 | True |

Seed2026100171, geometry minus full: CA-lDDT -0.00017,95% interval [-0.0012671289019819767, 0.0007745737119184515]; validity -0.00521.

Seed2026100181, geometry minus full: CA-lDDT +0.00066,95% interval [0.00025630913229489214, 0.0010768060448467264]; validity +0.00521.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
