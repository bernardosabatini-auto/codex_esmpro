# Paired ensemble development comparison

Candidate: state_scores_49643125/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.12500, +0.12500] |
| ca_lddt | 32 | 0.86711 | 0.86794 | -0.00083 | [-0.00377, +0.00243] |
| coarse_valid | 48 | 0.99154 | 0.99414 | -0.00260 | [-0.01823, +0.01237] |
| md_w1 | 16 | 0.47597 | 0.48850 | -0.01253 | [-0.02196, -0.00433] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
