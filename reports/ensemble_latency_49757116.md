# Matched ensemble latency

Status: complete.

Resident-model sequence-to-backbone latency, batch one sequence, K1/8/32, strict FP32. Includes sequence features, ESMC, trunk/flow, decoder, and output transfer. Teacher confidence heads omitted using validated early exit after backbone sampling. Loading, warmup, control comparisons and disk writes excluded from timed ranges.

Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.

| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |
|---|---:|---:|---:|---:|
| student | 0.6396 | 2.1350 | 7.5346 | 0.2224 |
| candidate | 0.4081 | 1.2044 | 4.0844 | 0.1186 |
| teacher | 1.4274 | 1.8555 | 3.5825 | 0.0695 |

Candidate uses 25 euler flow intervals, CFG1 with time power 1 and the same three-step decoder.


Ratios above one favor the candidate. Intervals resample paired sequence families, using each sequence’s three-repeat median; they do not include between-device variation.

| Comparator / candidate | Samples | Ratio | Paired95% interval |
|---|---:|---:|---|
| student / candidate | 1 | 1.5671 | [1.5537676249069892, 1.5817735467801595] |
| student / candidate | 8 | 1.7727 | [1.7664625243448466, 1.7778173264124357] |
| student / candidate | 32 | 1.8447 | [1.835993329041635, 1.8568466334180174] |
| teacher / candidate | 1 | 3.4975 | [1.4099981553971175, 5.64266724945428] |
| teacher / candidate | 8 | 1.5406 | [0.8226584569816003, 2.164381574249859] |
| teacher / candidate | 32 | 0.8771 | [0.609160987313637, 1.1184530120398324] |

This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Pipelines are measured sequentially on the same NVIDIA RTX PRO 6000 Blackwell Server Edition; repeat across devices before claiming a stable speed factor.
