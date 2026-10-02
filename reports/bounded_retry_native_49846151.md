# Bounded retry native pipeline

Separate64-family matched retry evaluation; all raw and attempted samples retained. Native qualification compares selected adapted outputs with selected original outputs. Historical raw failures remain unchanged.

| Head | Raw CA / valid | Retry CA / valid | Retry CA difference [95% CI] | Validity difference | Qualified |
|---|---|---|---|---:|---|
| original | 0.78384 / 0.97917 | 0.78436 / 0.98958 | +0.00000 [0.0, 0.0] | +0.00000 | True |
| seed2026100171_expansion | 0.79154 / 0.95312 | 0.79290 / 0.98958 | +0.00855 [0.00487400068350918, 0.012341506044839502] | +0.00000 | True |
| seed2026100181_expansion | 0.79182 / 0.96875 | 0.79343 / 0.99479 | +0.00907 [0.004687997006173528, 0.013492420097084143] | +0.00521 | True |

original: 202 attempted draws for192 outputs; 2 exhausted slots. Initial generation 66.02s plus retries 6.16s; peak 32.03GiB.

seed2026100171_expansion: 207 attempted draws for192 outputs; 2 exhausted slots. Initial generation 36.27s plus retries 5.47s; peak 35.03GiB.

seed2026100181_expansion: 203 attempted draws for192 outputs; 1 exhausted slots. Initial generation 36.27s plus retries 4.02s; peak 35.02GiB.

Single-pass generation times exclude ESM, loading and disk I/O; not an end-to-end latency benchmark. Native qualification still requires matched external diversity and efficiency evidence. Original34 and reserved17 unscored.
