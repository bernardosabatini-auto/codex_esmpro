# Paired ensemble development comparison

Candidate: reports/state_scores_49760580.json, cfg1/latent. Reference: reports/state_scores_49618816.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.09375, +0.00000] |
| ca_lddt | 32 | 0.87354 | 0.86794 | +0.00560 | [+0.00029, +0.01059] |
| coarse_valid | 48 | 0.99870 | 0.99414 | +0.00456 | [-0.00260, +0.01562] |
| md_w1 | 16 | 0.49422 | 0.48850 | +0.00572 | [-0.00255, +0.01429] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
