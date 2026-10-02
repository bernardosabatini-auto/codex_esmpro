# Antithetic versus IID external sampling

Same compact500 weights,32 outputs, guidance, precision, seed, decoder noise and retry cap; latent Gaussian draws differ only through sign pairing. All48 families and all16 eligible state families. Positive-draw and output-integrity controls passed.

| Selected metric | Antithetic | IID | Difference |95% family interval |
|---|---:|---:|---:|---|
| coverage_at_32 | 0.43750 | 0.43750 | +0.00000 | [0.0, 0.0] |
| both_states | 0.06250 | 0.06250 | +0.00000 | [0.0, 0.0] |
| ca_lddt | 0.87311 | 0.87286 | +0.00026 | [-0.00022425444515049355, 0.000774665424373181] |
| coarse_valid | 1.00000 | 1.00000 | +0.00000 | [0.0, 0.0] |
| md_w1 | 0.48953 | 0.48941 | +0.00012 | [-0.0014985613316655612, 0.0022161014055159314] |

Sampling quality:True; declared diversity-gain follow-up criterion:False.
Attempted draws/output1.00391; recovered6/6, exhausted0; generation130.92s plus retries1.31s.

MD W1 is better when lower. These development comparisons do not establish equilibrium populations. No end-to-end latency claim from generation-only timing. No pairing/temperature/seed-search grid. Locked tests unscored.
