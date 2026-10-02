# Bounded retry native pipeline

Separate64-family matched retry evaluation; all raw and attempted samples retained. Native qualification compares selected adapted outputs with selected original outputs. Historical raw failures remain unchanged.

| Head | Raw CA / valid | Retry CA / valid | Retry CA difference [95% CI] | Validity difference | Qualified |
|---|---|---|---|---:|---|
| original | 0.78384 / 0.97917 | 0.78436 / 0.98958 | +0.00000 [0.0, 0.0] | +0.00000 | True |
| compact500 | 0.79427 / 0.97396 | 0.79499 / 0.98958 | +0.01064 [0.005744284369727589, 0.0152867219354915] | +0.00000 | True |
| seed2026100171_balanced | 0.79902 / 0.96354 | 0.80089 / 0.99479 | +0.01653 [0.012106078582200254, 0.021270796060308947] | +0.00521 | True |
| seed2026100181_balanced | 0.79889 / 0.96875 | 0.79979 / 1.00000 | +0.01543 [0.011247737711678247, 0.01991224398827063] | +0.01042 | True |

original: 202 attempted draws for192 outputs; 2 exhausted slots. Initial generation 66.29s plus retries 6.17s; peak 32.03GiB.

compact500: 203 attempted draws for192 outputs; 2 exhausted slots. Initial generation 36.39s plus retries 3.70s; peak 35.03GiB.

seed2026100171_balanced: 204 attempted draws for192 outputs; 1 exhausted slots. Initial generation 36.37s plus retries 4.36s; peak 35.03GiB.

seed2026100181_balanced: 203 attempted draws for192 outputs; 0 exhausted slots. Initial generation 36.37s plus retries 4.94s; peak 35.02GiB.

Single-pass generation times exclude ESM, loading and disk I/O; not an end-to-end latency benchmark. Native qualification still requires matched external diversity and efficiency evidence. Original34 and reserved17 unscored.
