# Paired ensemble development comparison

Candidate: state_scores_49647134/score.json, cfg2/latent. Reference: state_scores_49647059/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, +0.09375] |
| ca_lddt | 32 | 0.86800 | 0.86446 | +0.00354 | [+0.00188, +0.00517] |
| coarse_valid | 48 | 0.98633 | 0.98177 | +0.00456 | [-0.00195, +0.01302] |
| md_w1 | 16 | 0.46132 | 0.46818 | -0.00686 | [-0.02088, +0.00621] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
