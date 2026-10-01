# Paired ensemble development comparison

Candidate: state_scores_49643175/score.json, cfg2/latent. Reference: state_scores_49643056/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.40625 | 0.43750 | -0.03125 | [-0.09375, +0.00000] |
| ca_lddt | 32 | 0.86712 | 0.86450 | +0.00262 | [+0.00192, +0.00334] |
| coarse_valid | 48 | 0.99089 | 0.98958 | +0.00130 | [-0.00130, +0.00391] |
| md_w1 | 16 | 0.47027 | 0.47734 | -0.00708 | [-0.01901, +0.00064] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
