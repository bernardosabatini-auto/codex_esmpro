# Matched ensemble latency

Status: complete.

Resident-model sequence-to-backbone latency, batch one sequence, K1/8/32, strict FP32. Includes sequence features, ESMC, trunk/flow, decoder, and output transfer. Teacher confidence heads omitted using validated early exit after backbone sampling. Loading, warmup, control comparisons and disk writes excluded from timed ranges.

Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.

| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |
|---|---:|---:|---:|---:|
| student | 0.8308 | 2.2360 | 7.3018 | 0.2087 |
| teacher | 1.3887 | 1.8201 | 3.8591 | 0.0797 |

This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Student and teacher are measured sequentially on the same H200; repeat across devices before claiming a stable speed factor.
