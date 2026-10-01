# GPU allocation accounting

Only registered single-GPU jobs. Allocation-normalized measured SM issue is capture-average SM issue times capture duration divided by total Slurm elapsed time. Unmeasured time contributes zero, so startup/export overhead is included conservatively. This is an instruction-issue indicator, not measured peak-FLOP efficiency.

| Job | Arm | Allocated minutes | Capture SM issue % | Work SM issue % | Allocation-normalized measured SM issue % | Peak reserved GiB |
|---|---|---:|---:|---:|---:|---:|
| 49654680 | cached_reference | 71.12 | 58.29 | 60.39 | 58.05 | 63.65 |
| 49654703 | cached_aligned_empirical | 70.93 | unavailable | unavailable | unavailable | 63.65 |

Job 49654703: incomplete counter coverage: collect::distill_train::0::500: 0.6756417399829576. No utilization estimate is assigned.
