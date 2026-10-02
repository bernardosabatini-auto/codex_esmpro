# Conditional latent repair: training feasibility

Status: complete; both-seed qualification: False.

All122 training families ×32 saved samples at each of two seeds. Only invalid outputs undergo bounded12-step latent optimization with the same decoder noise. Valid outputs and failed repairs remain exactly unchanged. This does not qualify raw models, native accuracy, external diversity, or physical plausibility.

| Training job | Invalid | Repaired | Fraction | Mean s/32 | Max s/32 | Feasible |
|---|---:|---:|---:|---:|---:|---|
| 49753133 | 14 | 0 | 0.0000 | 0.2062 | 4.6305 | False |
| 49753251 | 11 | 0 | 0.0000 | 0.1660 | 5.4799 | False |

GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition; peak reserved2.297GiB; elapsed82.92s.

All-family CPU screening plus conditional GPU repair, including conservative saved-output identity checks; excludes input/output disk, initial loading and valid-control checks.
