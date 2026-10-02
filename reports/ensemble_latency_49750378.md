# Matched ensemble latency

Status: complete.

Resident-model sequence-to-backbone latency, batch one sequence, K1/8/32, strict FP32. Includes sequence features, ESMC, trunk/flow, decoder, and output transfer. Teacher confidence heads omitted using validated early exit after backbone sampling. Loading, warmup, control comparisons and disk writes excluded from timed ranges.

Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.

| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |
|---|---:|---:|---:|---:|
| student | 0.8188 | 2.2367 | 7.3097 | 0.2094 |
| candidate | 0.7437 | 1.9964 | 6.4998 | 0.1857 |
| teacher | 1.3790 | 1.8147 | 3.8541 | 0.0798 |

Candidate uses 22 euler flow intervals, CFG2 with time power 1 and the same three-step decoder.


Ratios above one favor the candidate. Intervals resample paired sequence families, using each sequence’s three-repeat median; they do not include between-device variation.

| Comparator / candidate | Samples | Ratio | Paired95% interval |
|---|---:|---:|---|
| student / candidate | 1 | 1.1009 | [1.097982704629704, 1.1046125857638187] |
| student / candidate | 8 | 1.1204 | [1.118614873279285, 1.1223999884579747] |
| student / candidate | 32 | 1.1246 | [1.123571088028136, 1.1257985413239513] |
| teacher / candidate | 1 | 1.8542 | [0.9729825201530313, 2.836210403938707] |
| teacher / candidate | 8 | 0.9090 | [0.5406121814068636, 1.2698767896551684] |
| teacher / candidate | 32 | 0.5930 | [0.4143653326097698, 0.742176125623792] |

This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Pipelines are measured sequentially on the same NVIDIA H200; repeat across devices before claiming a stable speed factor.
