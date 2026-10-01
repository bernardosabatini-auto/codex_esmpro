# Teacher-label exposure diagnostic

Replayed training prefix: 2000 updates; 82 logged batch hashes match exactly.

The complete target/label sequence is reconstructed from the training algorithm and seeds, checked against every saved batch hash. Time/conditioning counts below are analytic expectations; CUDA draws were not replayed. All noise times contribute to training. Time>0.75 is a diagnostic region where the finite-teacher oracle strongly resolves states, not a cutoff for useful learning.

| Padded length | Proteins | Mean examples/protein | Singleton states | Mean draws/singleton | Mean expected conditioned examples at t>0.75 | Initial singleton hits | Current singleton hits |
|---|---:|---:|---:|---:|---:|---:|---:|
| 128 | 5 | 3200.00 | 8 | 192.25 | 23.53 | 4 | 1 |
| 256 | 9 | 888.89 | 3 | 57.67 | 7.06 | 2 | 1 |
| 384 | 9 | 444.44 | 19 | 29.32 | 3.59 | 11 | 6 |
| 512 | 9 | 444.44 | 21 | 28.38 | 3.47 | 10 | 7 |

Default P(t>0.75)=0.13597; shifting logistic-normal mean to1 would make it 0.46072. This arithmetic is not evidence that changing the time distribution improves the model. Prior-preserving time weighting remains a possible targeted follow-up if final capacity results warrant it.

The observed length pattern must be considered alongside exposure. More exposure alone is not a sufficient diagnosis of why an individual teacher state is missed; do not infer that late-time resampling will fix the failure from these counts.
