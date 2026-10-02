# Larger-data tuning quality

Status: complete; checkpoint2000.

Unchanged64-family tuning panel,3samples,FP32/Euler25/AE3. Both seeds retained; invalid samples remain included. No locked tests or model promotion.

| Head | CA-lDDT | Difference |95% interval | Valid | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_expansion_cfg1 | 0.79154 | +0.00770 | [0.003983083667773218, 0.011534049867245752] | 0.95312 | -0.02604 | False |
| seed2026100181_expansion_cfg1 | 0.79182 | +0.00799 | [0.003849699419948195, 0.012104664354544922] | 0.96875 | -0.01042 | False |

Replicated quality: False. Each qualified head still requires external diversity evaluation.
