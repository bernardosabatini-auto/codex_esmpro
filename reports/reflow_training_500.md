# Short-sampler tuning at 500 updates

64 tuning families, three seeds; baseline25/CFG2 versus learned5/10-step CFG1. One training seed; state coverage and measured latency still required.

| Arm | Steps | CA-lDDT | Delta versus initial | 95% family interval | Coarse validity | Native screen |
|---|---:|---:|---:|---|---:|---|
| reflow_paired | 5 | 0.77750 | -0.00634 | [-0.01557, +0.00164] | 0.77083 | False |
| reflow_paired | 10 | 0.79019 | +0.00635 | [-0.00023, +0.01174] | 0.94792 | False |
| reflow_independent | 5 | 0.77229 | -0.01155 | [-0.02132, -0.00278] | 0.61458 | False |
| reflow_independent | 10 | 0.79164 | +0.00780 | [+0.00393, +0.01161] | 0.92188 | False |

The TM diagnostic here uses Kabsch alignment. Optimized fixed-correspondence TM is scored separately. This screen alone cannot promote a sampler.
