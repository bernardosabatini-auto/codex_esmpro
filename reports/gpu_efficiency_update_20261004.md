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
