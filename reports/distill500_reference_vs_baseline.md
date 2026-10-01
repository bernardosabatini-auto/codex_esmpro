# Paired ensemble development comparison

Candidate: state_scores_49643056/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.12500, +0.12500] |
| ca_lddt | 32 | 0.86450 | 0.86794 | -0.00344 | [-0.00616, -0.00039] |
| coarse_valid | 48 | 0.98958 | 0.99414 | -0.00456 | [-0.02083, +0.00911] |
| md_w1 | 16 | 0.47734 | 0.48850 | -0.01115 | [-0.01837, -0.00433] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
