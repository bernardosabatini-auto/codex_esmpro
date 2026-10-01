# Teacher-label exposure diagnostic

Replayed training prefix: 500 updates; 21 logged batch hashes match exactly.

The complete target/label sequence is reconstructed from the training algorithm and seeds, checked against every saved batch hash. Time/conditioning counts below are analytic expectations; CUDA draws were not replayed. All noise times contribute to training. Time>0.75 is a diagnostic region where the finite-teacher oracle strongly resolves states, not a cutoff for useful learning.

| Padded length | Proteins | Mean examples/protein | Singleton states | Mean draws/singleton | Mean expected conditioned examples at t>0.75 | Initial singleton hits | Current singleton hits |
|---|---:|---:|---:|---:|---:|---:|---:|
| 128 | 5 | 800.00 | 8 | 48.75 | 5.97 | 4 | 1 |
| 256 | 9 | 222.22 | 3 | 16.00 | 1.96 | 2 | 1 |
| 384 | 9 | 111.11 | 19 | 6.79 | 0.83 | 11 | 8 |
| 512 | 9 | 111.11 | 21 | 6.62 | 0.81 | 10 | 11 |

Default P(t>0.75)=0.13597; shifting logistic-normal mean to1 would make it 0.46072. This arithmetic is not evidence that changing the time distribution improves the model. Prior-preserving time weighting remains a possible targeted follow-up if final capacity results warrant it.

The observed length pattern must be considered alongside exposure. More exposure alone is not a sufficient diagnosis of why an individual teacher state is missed; do not infer that late-time resampling will fix the failure from these counts.
