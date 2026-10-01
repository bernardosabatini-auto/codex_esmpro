# Short-sampler tuning at 2000 updates

64 tuning families, three seeds; baseline25/CFG2 versus specified learned CFG1 step counts. One training seed; state coverage and measured latency still required.

| Arm | Steps | CA-lDDT | Delta versus initial | 95% family interval | Coarse validity | Native screen |
|---|---:|---:|---:|---|---:|---|
| reflow_paired | 15 | 0.79221 | +0.00837 | [+0.00459, +0.01238] | 0.94792 | False |
| reflow_paired | 20 | 0.79176 | +0.00792 | [+0.00410, +0.01199] | 0.96354 | False |
| reflow_independent | 15 | 0.78963 | +0.00579 | [+0.00162, +0.00945] | 0.91146 | False |
| reflow_independent | 20 | 0.78914 | +0.00530 | [+0.00024, +0.00964] | 0.94792 | False |

The TM diagnostic here uses Kabsch alignment. Optimized fixed-correspondence TM is scored separately. This screen alone cannot promote a sampler.
