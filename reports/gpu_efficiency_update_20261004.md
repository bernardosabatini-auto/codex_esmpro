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

The compatible-fragment diagnostic50364419 used one RTX for1:13 and generated512
backbones in a58.44s worker. Its short capture measured32.19% composite over20valid
seconds (SM54.57%,DRAM31.38%,tensor0). The subsequent281.86s of closure solver
work ran on CPU after GPU release. Short necessary diagnostics carry proportionally
more startup overhead; prolonging them would waste allocated GPU time.

The new context-refresh frame preflight likewise verifies source content on CPU
before submission, checks bound file metadata at GPU startup/end, and independently
rehashes and scores outputs on CPU after allocation release. Its source verification
is not billed to GPU time. This preparation pattern preserves content audits without
repeating the full input scan inside the GPU allocation.

Wider-context-mask training50376770 completed2,000updates in698.46s, released one
RTX after13:25 and reserved37.17GiB. Assigned-UUID DCGM measured50.37% composite
over746valid seconds:84.56%SM,57.37%DRAM,93.03%graphics engine and0%tensor. This
is captured activity, not the account24-hour metric. Full run source verification
and training-data preparation occurred before allocation; independent scoring and
all256generated/control CPUclosures run after GPU release.

Fixed-scaffold bridge training50385481 completed2,000updates in690.12s and released
one RTX after13:06. Its737valid captured seconds measured51.01% composite:
85.66%SM,58.13%DRAM,94.03%graphics engine and0%tensor. The worker took769.62s,
including generation and numerical controls. CPU preparation and subsequent
independent scoring/256closure calculations remain outside the GPU allocation.
These captures exclude recorder startup and do not reproduce the dashboard's
24-hour hourly-allocation statistic. No other agents' jobs were inspected.
