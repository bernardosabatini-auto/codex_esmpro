# GPU efficiency update — 2026-10-04

Assigned-UUID DCGM capture, using the user's exact composite:
0.35 SM + 0.35 tensor + 0.20 DRAM + 0.10 graphics engine.

| Workload | Captured real utilization | SM active | DRAM active | Valid seconds |
|---|---:|---:|---:|---:|
| 2,000-update inpainting training,50344679 | 51.44% | 86.40% | 58.64% | 729 |
| Eight matched refold jobs | 42.03% | 73.99% | 36.97% | 5629 |

Refold jobs: 50347943, 50348218, 50348429, 50348749, 50348089, 50348300, 50348540, 50348920. Individual composites40.50–43.17%.
These are averages over captured seconds, excluding startup before instrumentation;
they are not the account's24-hour hourly-allocation dashboard. Only registered own jobs were inspected.

The FP32 training path registers zero tensor-pipeline activity; refolding about0.42%.
Memory activity is measured by DRAM counters, not occupied VRAM. Training reserves37.16GiB;
this is useful capacity headroom, not evidence of idle bandwidth.

Keep exactFP32 outputs, overlap CPU scoring with GPU refolding, reuse unchanged control
budgets, and release each allocation when work finishes. Do not add redundant work or
fill VRAM to raise the score. The prior confidence-head bypass saved only2.86%, below
its5% adoption threshold; it remains disabled. The new junction experiment uses the
same measured batches and first performs a40-update single-RTX numerical/runtime profile.

## New matched tests

Junction-weighted training50356015 completed2,000updates in687.95s and released its
single RTX after13:05. Assigned-UUID capture:51.21% real utilization across733valid
seconds,86.01%SM and58.33%DRAM active. First40raw/EMA weights match the profile exactly;
all2,000data/noise/time/dropout draws match the uniform-loss baseline.

The scientific endpoint failed:1/128generated backbones meets the connected raw gate
(required45). No1,024-refold budget is spent on that model.

Concurrency profile50357135 completed all64full-atom folds on one RTX. Independent
CPU audit confirms exact coordinate parity and identical post-fold RNG states against
the archived single-worker outputs. Two resident workers ran the same pairs sequentially
or concurrently. Sequential timed pairs took64.958s; concurrent pairs69.703s: **7.30%slower**.
The128bucket improved10.21%, but256/384/512 regressed7.38/7.42/8.77%. Reject this fixed
concurrency recipe; no end-to-end expansion. Peak reserved memory per worker29.64GiB.

The profile moves the24GiB dependency hash scan to CPU preparation, binds file size,
mtime and inode before/after content verification, checks them at GPU startup, and
performs full content verification again in the independent CPU completion audit.
This changes no model or sampling setting. It avoids GPU allocation during the redundant
hash scan; the speedup of that startup change was not separately timed. Existing
scientific refolding still uses its original input-validation path until a future
qualified pipeline applies this preparation pattern.
