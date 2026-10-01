# Paired ensemble development comparison

Candidate: state_scores_49647280/score.json, cfg2/latent. Reference: state_scores_49647059/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, +0.09375] |
| ca_lddt | 32 | 0.86760 | 0.86446 | +0.00314 | [+0.00149, +0.00480] |
| coarse_valid | 48 | 0.98763 | 0.98177 | +0.00586 | [-0.00065, +0.01497] |
| md_w1 | 16 | 0.46628 | 0.46818 | -0.00190 | [-0.01822, +0.01442] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
