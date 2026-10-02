# Larger-data tuning quality

Status: complete; checkpoint500.

Unchanged64-family tuning panel,3samples,FP32/Euler25/AE3. Both seeds retained; invalid samples remain included. No locked tests or model promotion.

| Head | CA-lDDT | Difference |95% interval | Valid | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_expansion_cfg1 | 0.77790 | -0.00593 | [-0.012769403408337645, -0.00020879631640586825] | 0.94792 | -0.03125 | False |
| seed2026100181_expansion_cfg1 | 0.78508 | +0.00124 | [-0.00479650587242008, 0.0067323380294395194] | 0.97917 | +0.00000 | True |

Replicated quality: False. Each qualified head still requires external diversity evaluation.
