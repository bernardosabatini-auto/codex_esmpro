# Paired ensemble development comparison

Candidate: state_scores_49820859/score.json, cfg1/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, +0.09375] |
| ca_lddt | 32 | 0.86736 | 0.86794 | -0.00057 | [-0.00523, +0.00368] |
| coarse_valid | 48 | 0.99870 | 0.99414 | +0.00456 | [-0.00195, +0.01497] |
| md_w1 | 16 | 0.48799 | 0.48850 | -0.00051 | [-0.01251, +0.01479] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
