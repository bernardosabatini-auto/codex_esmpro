# Paired ensemble development comparison

Candidate: state_scores_49822460/score.json, cfg1/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.34375 | 0.43750 | -0.09375 | [-0.18750, +0.00000] |
| ca_lddt | 32 | 0.87439 | 0.86794 | +0.00646 | [+0.00111, +0.01140] |
| coarse_valid | 48 | 0.99935 | 0.99414 | +0.00521 | [-0.00130, +0.01562] |
| md_w1 | 16 | 0.48907 | 0.48850 | +0.00057 | [-0.00666, +0.00754] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
