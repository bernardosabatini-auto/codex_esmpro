# Model complementarity in saved development samples

Exploratory CPU-only diagnostic, using every one of the16 two-state families. Three fixed32-output mixtures; no family-specific model choice or reference-informed sample selection. All constituent predictions are from the recorded retry pipelines.

| Fixed mixture | Coverage | Difference [95% CI] | Both-state families | CA-lDDT | Valid | Feasible |
|---|---:|---|---:|---:|---:|---|
| original_compact | 0.46875 | +0.03125 [0.0, 0.09375] | 1/16 | 0.89855 | 1.00000 | False |
| balanced_seeds | 0.34375 | -0.09375 [-0.1875, 0.0] | 0/16 | 0.90412 | 1.00000 | False |
| four_heads | 0.40625 | -0.03125 [-0.09375, 0.0] | 0/16 | 0.90147 | 1.00000 | False |

Observed union of all128 saved outputs/family: coverage0.46875, change+0.03125 interval[0.0, 0.09375] versus original32. This is a support bound for these saved draws, not a32-sample pipeline or a bound on future unseen noise draws.

A positive mixture feasibility result would still need native, all48-family MD and matched latency testing. Mixing multiple loaded heads adds model memory and inference cost; no efficiency claim from this CPU calculation. No mixing-weight grid. Original34 and reserved17 remain unscored.
