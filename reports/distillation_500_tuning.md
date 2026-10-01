# Matched training:500-update tuning checkpoint

Interim single-training-seed results,64 family-isolated tuning proteins and three fixed sampling seeds each. Reference coordinates are independently verified AFDB predictions. All four runs continue to2,000 updates; both checkpoints get separate ensemble-development evaluation.

| Arm | CA lDDT | Change from initial | 95% paired family interval | Coarse valid |
|---|---:|---:|---|---:|
| raw_reference | 0.78065 | -0.00319 | [-0.00774,+0.00117] | 0.96354 |
| reference | 0.78145 | -0.00239 | [-0.00742,+0.00302] | 0.94792 |
| empirical | 0.78639 | +0.00255 | [-0.00272,+0.00801] | 0.96354 |
| balanced | 0.78572 | +0.00188 | [-0.00279,+0.00655] | 0.95312 |

Initial CA lDDT:0.78384; initial coarse-valid fraction:0.97917. These tuning changes do not establish useful generative diversity or robust improvement. Geometry and state coverage on the frozen ensemble panel are required, followed by training-seed replication of eligible effects.

| Comparison against canonical reference-only | CA lDDT difference | 95% family interval |
|---|---:|---|
| raw_reference | -0.00080 | [-0.00414,+0.00226] |
| empirical | +0.00494 | [+0.00307,+0.00684] |
| balanced | +0.00427 | [+0.00184,+0.00653] |
