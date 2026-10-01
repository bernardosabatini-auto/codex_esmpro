# Matched training at 2000 updates

64 tuning families, three samples each; single training seed. TM is after Kabsch, not TM-align optimization. No ensemble promotion claim.

## ca_lddt

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.78027 | -0.00357 | [-0.00918, +0.00164] | +0.00102 | [-0.00340, +0.00497] |
| reference | 0.77925 | -0.00459 | [-0.00937, +0.00045] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.78694 | +0.00310 | [-0.00165, +0.00851] | +0.00769 | [+0.00462, +0.01100] |
| balanced | 0.78632 | +0.00248 | [-0.00195, +0.00742] | +0.00707 | [+0.00412, +0.01020] |

## tm_after_kabsch

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.53287 | -0.01242 | [-0.02912, +0.00429] | +0.01247 | [-0.00014, +0.02488] |
| reference | 0.52040 | -0.02489 | [-0.04230, -0.00811] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.52900 | -0.01629 | [-0.03086, -0.00211] | +0.00860 | [+0.00027, +0.01691] |
| balanced | 0.52568 | -0.01961 | [-0.03468, -0.00501] | +0.00528 | [-0.00202, +0.01253] |

## coarse_valid

| Arm | Mean | Change from initial | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---|---:|---|
| raw_reference | 0.97917 | +0.00000 | [+0.00000, +0.00000] | +0.01562 | [+0.00000, +0.04167] |
| reference | 0.96354 | -0.01562 | [-0.04167, +0.00000] | +0.00000 | [+0.00000, +0.00000] |
| empirical | 0.96354 | -0.01562 | [-0.03646, +0.00000] | -0.00000 | [-0.02083, +0.02083] |
| balanced | 0.96354 | -0.01562 | [-0.03646, +0.00000] | -0.00000 | [-0.02083, +0.02083] |

AFDB reference coordinates are predictions. Evaluate state coverage and validity separately on the frozen development ensemble panel before any replication or promotion. Reserved confirmation and original test remain unscored.
