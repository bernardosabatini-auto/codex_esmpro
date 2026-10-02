# Bounded retry native pipeline

Separate64-family matched retry evaluation; all raw and attempted samples retained. Native qualification compares selected adapted outputs with selected original outputs. Historical raw failures remain unchanged.

| Head | Raw CA / valid | Retry CA / valid | Retry CA difference [95% CI] | Validity difference | Qualified |
|---|---|---|---|---:|---|
| original | 0.78384 / 0.97917 | 0.78436 / 0.98958 | +0.00000 [0.0, 0.0] | +0.00000 | True |
| compact500 | 0.79427 / 0.97396 | 0.79499 / 0.98958 | +0.01064 [0.005744284369727589, 0.0152867219354915] | +0.00000 | True |
| compact500_antithetic | 0.79554 / 0.96875 | 0.79530 / 0.98958 | +0.01094 [0.006177089091382887, 0.015622451207672193] | +0.00000 | True |

original: 202 attempted draws for192 outputs; 2 exhausted slots. Initial generation 66.12s plus retries 6.13s; peak 32.03GiB.

compact500: 203 attempted draws for192 outputs; 2 exhausted slots. Initial generation 36.34s plus retries 3.68s; peak 35.03GiB.

compact500_antithetic: 202 attempted draws for192 outputs; 2 exhausted slots. Initial generation 36.33s plus retries 4.11s; peak 35.03GiB.

Single-pass generation times exclude ESM, loading and disk I/O; not an end-to-end latency benchmark. Native qualification still requires matched external diversity and efficiency evidence. Original34 and reserved17 unscored.

Antithetic versus selected compact IID: CA difference+0.00030,95% interval[-0.003322900330650275, 0.003428193148786785]; validity difference+0.00000. Both original and compact native criteria pass:True. Antithetic first output matches historical sample0; other first outputs intentionally use paired latent noise and remain fully included.
