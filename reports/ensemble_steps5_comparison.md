# Paired ensemble development comparison

Candidate: state_scores_49640022, cfg2/latent. Reference: state_scores_49618816, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.15625, +0.09375] |
| ca_lddt | 32 | 0.80127 | 0.86794 | -0.06667 | [-0.07822, -0.05645] |
| coarse_valid | 48 | 0.78385 | 0.99414 | -0.21029 | [-0.27799, -0.14648] |
| md_w1 | 16 | 0.45505 | 0.48850 | -0.03345 | [-0.05510, -0.00660] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
