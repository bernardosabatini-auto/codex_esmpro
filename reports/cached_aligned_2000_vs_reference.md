# Paired ensemble development comparison

Candidate: state_scores_49672377/score.json, cfg2/latent. Reference: state_scores_49672152/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.46875 | -0.03125 | [-0.09375, +0.00000] |
| ca_lddt | 32 | 0.86461 | 0.86402 | +0.00059 | [-0.00188, +0.00302] |
| coarse_valid | 48 | 0.98828 | 0.98828 | +0.00000 | [-0.00586, +0.00651] |
| md_w1 | 16 | 0.47530 | 0.48165 | -0.00635 | [-0.01388, +0.00113] |

Sampling quality gate: False. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
