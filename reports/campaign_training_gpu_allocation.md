# GPU allocation accounting

Only registered single-GPU jobs. Allocation-normalized measured SM issue is capture-average SM issue times capture duration divided by total Slurm elapsed time. Unmeasured time contributes zero, so startup/export overhead is included conservatively. This is an instruction-issue indicator, not measured peak-FLOP efficiency.

| Job | Arm | Allocated minutes | Capture SM issue % | Work SM issue % | Allocation-normalized measured SM issue % | Peak reserved GiB |
|---|---|---:|---:|---:|---:|---:|
| 49654680 | cached_reference | 71.12 | 58.29 | 60.39 | 58.05 | 63.65 |
| 49654703 | cached_aligned_empirical | 70.93 | unavailable | unavailable | unavailable | 63.65 |
| 49662855 | reflow_paired | 67.97 | 29.59 | 30.01 | 29.45 | 63.66 |
| 49662912 | reflow_independent | 68.10 | 59.52 | 60.39 | 59.29 | 63.66 |

Job 49654703: incomplete counter coverage: collect::distill_train::0::500: 0.6756417399829576. No utilization estimate is assigned.

Paired reflow has an unexplained 50% ceiling in SM-active counters versus 100% for the independent arm, despite similar training runtime, clocks and memory throughput. GPU UUIDs match each run's own telemetry. This is unresolved and does not justify rescaling counters or claiming the paired run met the 50% target.
