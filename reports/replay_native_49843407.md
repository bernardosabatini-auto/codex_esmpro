# Functional replay native quality

Status:complete; checkpoint500.427 teacher families plus390 disjoint anchor training families; unchanged64-family native tuning panel and3samples. All failures retained, locked tests unscored.

| Head | CA-lDDT | CA difference |95% interval | Valid | Validity difference | Qualified |
|---|---:|---:|---|---:|---:|---|
| original_cfg2 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True |
| seed2026100171_replay_cfg1 | 0.77605 | -0.00779 | [-0.015500588115861557, -0.0012265489653605888] | 0.96354 | -0.01562 | False |
| seed2026100181_replay_cfg1 | 0.77894 | -0.00490 | [-0.012174982283076341, 0.0017393020289517133] | 0.95312 | -0.02604 | False |

seed2026100171_replay_cfg1 versus same-step plain427: CA difference-0.00185,95% interval[-0.00394388546951411, 0.0004117617457931902]; validity difference+0.01562.

seed2026100181_replay_cfg1 versus same-step plain427: CA difference-0.00614,95% interval[-0.011404361090472128, -0.002550482752778708]; validity difference-0.02604.

Replicated native quality:False. Each individually qualified head still requires external diversity evaluation.
