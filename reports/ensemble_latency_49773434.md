# Matched ensemble latency

Status: failed.

None

Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.

| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |
|---|---:|---:|---:|---:|

Missing manifest

This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Pipelines are measured sequentially on the same unreported; repeat across devices before claiming a stable speed factor.
