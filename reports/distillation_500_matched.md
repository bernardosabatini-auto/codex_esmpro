# Matched training at 500 updates

64 tuning families, three samples each; single training seed. TM is after Kabsch, not TM-align optimization. No ensemble promotion claim.

## ca_lddt

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.78065 | -0.00319 | [-0.00774, +0.00117] | -0.00080 | [-0.00414, +0.00226] |
| reference | 0.78145 | -0.00239 | [-0.00742, +0.00302] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.78639 | +0.00255 | [-0.00272, +0.00801] | +0.00494 | [+0.00307, +0.00684] |
| balanced | 0.78572 | +0.00188 | [-0.00279, +0.00655] | +0.00427 | [+0.00184, +0.00653] |

## tm_after_kabsch

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.52503 | -0.02026 | [-0.03363, -0.00731] | +0.00360 | [-0.00400, +0.01124] |
| reference | 0.52143 | -0.02386 | [-0.03669, -0.01142] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.52880 | -0.01649 | [-0.02856, -0.00515] | +0.00737 | [+0.00353, +0.01133] |
| balanced | 0.52702 | -0.01827 | [-0.02943, -0.00747] | +0.00560 | [+0.00121, +0.00987] |

## coarse_valid

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.96354 | -0.01562 | [-0.03646, +0.00000] | +0.01562 | [-0.00521, +0.03646] |
| reference | 0.94792 | -0.03125 | [-0.05729, -0.01042] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.96354 | -0.01562 | [-0.03646, +0.00000] | +0.01562 | [-0.00521, +0.03646] |
| balanced | 0.95312 | -0.02604 | [-0.04688, -0.00521] | +0.00521 | [-0.01562, +0.02604] |

AFDB reference coordinates are predictions. Evaluate state coverage and validity separately on the frozen development ensemble panel before any replication or promotion. Reserved confirmation and original test remain unscored.
