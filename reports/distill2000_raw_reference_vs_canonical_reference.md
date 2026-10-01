# Paired ensemble development comparison

Candidate: state_scores_49646851/score.json, cfg2/latent. Reference: state_scores_49647059/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.09375, +0.00000] |
| ca_lddt | 32 | 0.86366 | 0.86446 | -0.00079 | [-0.00263, +0.00095] |
| coarse_valid | 48 | 0.97982 | 0.98177 | -0.00195 | [-0.01432, +0.00846] |
| md_w1 | 16 | 0.47565 | 0.46818 | +0.00748 | [+0.00044, +0.01541] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
