# Paired ensemble development comparison

Candidate: state_scores_49646851/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.12500, +0.06250] |
| ca_lddt | 32 | 0.86366 | 0.86794 | -0.00428 | [-0.00679, -0.00146] |
| coarse_valid | 48 | 0.97982 | 0.99414 | -0.01432 | [-0.04557, +0.00781] |
| md_w1 | 16 | 0.47565 | 0.48850 | -0.01284 | [-0.02001, -0.00561] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
