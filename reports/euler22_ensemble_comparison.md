# Paired ensemble development comparison

Candidate: state_scores_49746205/score.json, cfg2/latent. Reference: state_scores_49618816/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [+0.00000, +0.00000] |
| ca_lddt | 32 | 0.86613 | 0.86794 | -0.00181 | [-0.00299, -0.00071] |
| coarse_valid | 48 | 0.99414 | 0.99414 | +0.00000 | [-0.00260, +0.00260] |
| md_w1 | 16 | 0.48746 | 0.48850 | -0.00103 | [-0.00791, +0.00526] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
