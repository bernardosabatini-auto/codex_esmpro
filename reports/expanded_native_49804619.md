# Direct decoded geometry training: separate accuracy transfer

Status: complete; checkpoint 500.

64 separate tuning families, three paired samples. Full balanced122 controls and direct decoded-geometry training at both seeds, CFG1 versus originalCFG2. Euler25/decoder3, strict FP32, all samples retained. No output repair or independent-test scoring. Unadjusted family intervals.

| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_full_cfg1 | 0.78794 | +0.00410 | [-0.001569854335074207, 0.00901624221794908] | 0.95312 | -0.02604 | False |
| seed2026100171_geometry_cfg1 | 0.78963 | +0.00579 | [0.0022842472315489047, 0.009500422741074514] | 0.95312 | -0.02604 | False |
| seed2026100181_full_cfg1 | 0.78827 | +0.00443 | [-0.001620546576334707, 0.009320844237129722] | 0.96354 | -0.01562 | False |
| seed2026100181_geometry_cfg1 | 0.78884 | +0.00500 | [-0.001141444320152488, 0.009950150458184464] | 0.96354 | -0.01562 | False |

Seed2026100171, geometry minus full: CA-lDDT +0.00169,95% interval [-0.0007995456693445493, 0.005831907903261732]; validity +0.00000.

Seed2026100181, geometry minus full: CA-lDDT +0.00056,95% interval [0.00013227432555104236, 0.0010141238167679508]; validity -0.00000.

Both candidate seeds qualify: False. External experimental-state ensembles remain a separate test; no model promotion.
