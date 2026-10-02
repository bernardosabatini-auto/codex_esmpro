# Bounded retry native pipeline

Separate64-family matched retry evaluation; all raw and attempted samples retained. Native qualification compares selected adapted outputs with selected original outputs. Historical raw failures remain unchanged.

| Head | Raw CA / valid | Retry CA / valid | Retry CA difference [95% CI] | Validity difference | Qualified |
|---|---|---|---|---:|---|
| original | 0.78384 / 0.97917 | 0.78436 / 0.98958 | +0.00000 [0.0, 0.0] | +0.00000 | True |
| compact500 | 0.79427 / 0.97396 | 0.79499 / 0.98958 | +0.01064 [0.005744284369727589, 0.0152867219354915] | +0.00000 | True |
| reflow10 | 0.79060 / 0.94792 | 0.79155 / 0.98438 | +0.00719 [0.002947967889091623, 0.011396559206404136] | -0.00521 | True |

original: 202 attempted draws for192 outputs; 2 exhausted slots. Initial generation 66.41s plus retries 6.16s; peak 32.03GiB.

compact500: 203 attempted draws for192 outputs; 2 exhausted slots. Initial generation 36.27s plus retries 3.69s; peak 35.03GiB.

reflow10: 212 attempted draws for192 outputs; 3 exhausted slots. Initial generation 18.55s plus retries 3.69s; peak 35.02GiB.

Single-pass generation times exclude ESM, loading and disk I/O; not an end-to-end latency benchmark. Native qualification still requires matched external diversity and efficiency evidence. Original34 and reserved17 unscored.

original versus selectedcompact500: CA difference-0.01064,95% interval[-0.0152867219354915, -0.005744284369727589]; validity difference+0.00000.

compact500 versus selectedcompact500: CA difference+0.00000,95% interval[0.0, 0.0]; validity difference+0.00000.

reflow10 versus selectedcompact500: CA difference-0.00344,95% interval[-0.008424156429651709, 0.0013691323433698628]; validity difference-0.00521.
