# Paired ensemble development comparison

Candidate: state_scores_49660888/score.json, cfg2/latent. Reference: state_scores_49660833/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.46875 | 0.46875 | +0.00000 | [+0.00000, +0.00000] |
| ca_lddt | 32 | 0.86631 | 0.86266 | +0.00365 | [+0.00128, +0.00634] |
| coarse_valid | 48 | 0.99284 | 0.98763 | +0.00521 | [-0.00130, +0.01367] |
| md_w1 | 16 | 0.47598 | 0.48682 | -0.01084 | [-0.02192, -0.00178] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
