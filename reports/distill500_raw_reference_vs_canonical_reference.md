# Paired ensemble development comparison

Candidate: state_scores_49642986/score.json, cfg2/latent. Reference: state_scores_49643056/score.json, cfg2/latent.

| Metric | Families | Candidate | Reference | Difference | 95% family interval |
|---|---:|---:|---:|---:|---|
| coverage_at_32 | 16 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, +0.09375] |
| ca_lddt | 32 | 0.86422 | 0.86450 | -0.00028 | [-0.00149, +0.00089] |
| coarse_valid | 48 | 0.99023 | 0.98958 | +0.00065 | [-0.00456, +0.00521] |
| md_w1 | 16 | 0.48022 | 0.47734 | +0.00288 | [-0.00094, +0.00694] |

Sampling quality gate: True. Training diversity gate: False.

MD W1 is better when lower; other metrics are better when higher. CA lDDT uses each sample’s closest observed reference state, not best-of-K sample selection. Gate results are development screens, not confirmation or independent-test claims. Training promotion additionally requires native-accuracy checks and training-seed replication. A sampling candidate also requires matched end-to-end timing.
