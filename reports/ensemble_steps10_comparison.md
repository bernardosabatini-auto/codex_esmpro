# Paired ensemble development comparison

Candidate: state_scores_49640046, cfg2/latent. Reference: state_scores_49618816, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.12500, +0.06250] |
| ca_lddt | 32 | 0.85005 | 0.86794 | -0.01789 | [-0.02269, -0.01334] |
| coarse_valid | 48 | 0.98503 | 0.99414 | -0.00911 | [-0.02476, +0.00260] |
| md_w1 | 16 | 0.48264 | 0.48850 | -0.00586 | [-0.01597, +0.00956] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
