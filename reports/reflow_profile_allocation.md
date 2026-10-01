# GPU allocation accounting

Only registered single-GPU jobs. Allocation-normalized measured SM issue is capture-average SM issue times capture duration divided by total Slurm elapsed time. Unmeasured time contributes zero, so startup/export overhead is included conservatively. This is an instruction-issue indicator, not measured peak-FLOP efficiency.

| Job | Arm | Allocated minutes | Capture SM issue % | Work SM issue % | Allocation-normalized measured SM issue % | Peak reserved GiB |
|---|---|---:|---:|---:|---:|---:|
| 49655628 | data/profile | 11.48 | 55.96 | 69.57 | 53.76 | 15.20 |
| 49657893 | data/profile | 10.10 | unavailable | unavailable | unavailable | 15.25 |
| 49658005 | data/profile | 11.13 | 57.72 | 69.90 | 55.76 | 15.04 |
| 49658117 | data/profile | 11.42 | 56.34 | 69.55 | 54.54 | 15.25 |
| 49657719 | reflow_paired | 2.43 | 33.24 | 59.68 | 31.83 | 64.96 |

Job 49657893: incomplete counter coverage: collect::reflow_pairs::41: 0.5723780417873982. No utilization estimate is assigned.
