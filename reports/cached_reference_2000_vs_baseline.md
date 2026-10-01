# Paired ensemble development comparison

Candidate: state_scores_49672152/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.46875 | 0.43750 | +0.03125 | [+0.00000, +0.09375] |
| ca_lddt | 32 | 0.86402 | 0.86794 | -0.00391 | [-0.00644, -0.00180] |
| coarse_valid | 48 | 0.98828 | 0.99414 | -0.00586 | [-0.01302, -0.00065] |
| md_w1 | 16 | 0.48165 | 0.48850 | -0.00685 | [-0.01849, +0.00119] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
