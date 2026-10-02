# Paired ensemble development comparison

Candidate: state_scores_49771176/score.json, cfg1/latent. Reference: state_scores_49742947/score.json, cfg1/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [+0.00000, +0.00000] |
| ca_lddt | 32 | 0.87248 | 0.87248 | +0.00000 | [+0.00000, +0.00000] |
| coarse_valid | 48 | 0.99609 | 0.99609 | +0.00000 | [+0.00000, +0.00000] |
| md_w1 | 16 | 0.48432 | 0.48432 | -0.00000 | [-0.00000, +0.00000] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
