# Matched ensemble latency

Status: complete.

Resident-model sequence-to-backbone latency, batch one sequence, K1/8/32, strict FP32. Includes sequence features, ESMC, trunk/flow, decoder, and output transfer. Teacher confidence heads omitted using validated early exit after backbone sampling. Loading, warmup, control comparisons and disk writes excluded from timed ranges.

Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.

| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |
|---|---:|---:|---:|---:|
| student | 0.6480 | 2.1281 | 7.4170 | 0.2184 |
| expanded_candidate | 0.4142 | 1.2021 | 4.0293 | 0.1166 |
| candidate | 0.4120 | 1.1373 | 3.7314 | 0.1071 |
| teacher | 1.4429 | 1.8668 | 3.6044 | 0.0697 |

Candidate uses 25 euler flow intervals, CFG1 with time power 1 and the same three-step decoder.


Candidate uses compact single-sequence conditioning in strict FP32. The expanded_candidate comparator, when present, uses identical weights and sampler with expanded conditioning on the same GPU.

Ratios above one favor the candidate. Intervals resample paired sequence families, using each sequence’s three-repeat median; they do not include between-device variation.

| Comparator / candidate | Samples | Ratio | Paired95% interval |
|---|---:|---:|---|
| student / candidate | 1 | 1.5730 | [1.5563668034105174, 1.5970666190694585] |
| student / candidate | 8 | 1.8712 | [1.8084206763389796, 1.9119223897228808] |
| student / candidate | 32 | 1.9877 | [1.9340132643972603, 2.0159216843999404] |
| expanded_candidate / candidate | 1 | 1.0055 | [0.9960867044741899, 1.0183597752700713] |
| expanded_candidate / candidate | 8 | 1.0570 | [1.0215637168427407, 1.0786410833068403] |
| expanded_candidate / candidate | 32 | 1.0798 | [1.0445487938230829, 1.0995102665888494] |
| teacher / candidate | 1 | 3.5024 | [1.4734898924284587, 5.593714567263474] |
| teacher / candidate | 8 | 1.6414 | [0.858753240721601, 2.334025123601148] |
| teacher / candidate | 32 | 0.9660 | [0.6637218641338034, 1.2417859438086016] |

This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Pipelines are measured sequentially on the same NVIDIA RTX PRO 6000 Blackwell Server Edition; repeat across devices before claiming a stable speed factor.
