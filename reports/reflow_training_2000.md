# Short-sampler tuning at 2000 updates

64 tuning families, three seeds; baseline25/CFG2 versus specified learned CFG1 step counts. One training seed; state coverage and measured latency still required.

| Arm | Steps | CA-lDDT | Delta versus initial | 95% family interval | Coarse validity | Native screen |
|---|---:|---:|---:|---|---:|---|
| reflow_paired | 5 | 0.78195 | -0.00189 | [-0.01037, +0.00538] | 0.82292 | False |
| reflow_paired | 10 | 0.79060 | +0.00676 | [+0.00247, +0.01095] | 0.94792 | False |
| reflow_independent | 5 | 0.75814 | -0.02570 | [-0.04156, -0.01115] | 0.61458 | False |
| reflow_independent | 10 | 0.78578 | +0.00195 | [-0.00555, +0.00797] | 0.85938 | False |

The TM diagnostic here uses Kabsch alignment. Optimized fixed-correspondence TM is scored separately. This screen alone cannot promote a sampler.
