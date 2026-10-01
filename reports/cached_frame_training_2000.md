# Matched training at 2000 updates

64 tuning families, three samples each; single training seed. TM is after Kabsch, not TM-align optimization. No ensemble promotion claim.

## ca_lddt

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.77774 | -0.00610 | [-0.01051, -0.00184] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.78758 | +0.00374 | [-0.00078, +0.00885] | +0.00984 | [+0.00600, +0.01385] |

## tm_after_kabsch

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.54348 | -0.00181 | [-0.01480, +0.01030] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.54803 | +0.00274 | [-0.00617, +0.01156] | +0.00455 | [-0.00641, +0.01540] |

## coarse_valid

| Arm | Mean | Change from initial | 95% family interval | Change from matched reference | 95% family interval |
|---|---:|---:|---|---:|---|
| cached_reference | 0.95312 | -0.02604 | [-0.05729, -0.00521] | +0.00000 | [+0.00000, +0.00000] |
| cached_aligned_empirical | 0.95833 | -0.02083 | [-0.04167, -0.00521] | +0.00521 | [-0.01563, +0.02604] |

AFDB reference coordinates are predictions. Evaluate state coverage and validity separately on the frozen development ensemble panel before any replication or promotion. Reserved confirmation and original test remain unscored.
