# Matched training at 500 updates

64 tuning families, three samples each; single training seed. TM is after Kabsch, not TM-align optimization. No ensemble promotion claim.

## ca_lddt

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.77857 | -0.00526 | [-0.00832, -0.00245] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.78729 | +0.00345 | [-0.00131, +0.00807] | +0.00871 | [+0.00433, +0.01315] |

## tm_after_kabsch

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.54361 | -0.00168 | [-0.00908, +0.00513] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.54975 | +0.00446 | [-0.00463, +0.01365] | +0.00614 | [-0.00418, +0.01669] |

## coarse_valid

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.96875 | -0.01042 | [-0.02604, +0.00000] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.96354 | -0.01562 | [-0.04167, +0.00000] | -0.00521 | [-0.02604, +0.01042] |

AFDB reference coordinates are predictions. Evaluate state coverage and validity separately on the frozen development ensemble panel before any replication or promotion. Reserved confirmation and original test remain unscored.
