# Paired ensemble development comparison

Candidate: state_scores_49642986/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, +0.09375] |
| ca_lddt | 32 | 0.86422 | 0.86794 | -0.00371 | [-0.00586, -0.00129] |
| coarse_valid | 48 | 0.99023 | 0.99414 | -0.00391 | [-0.02083, +0.01172] |
| md_w1 | 16 | 0.48022 | 0.48850 | -0.00828 | [-0.01453, -0.00196] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
