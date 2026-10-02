# Inner refinement self-conditioning

Status: complete.

All16families/four seeds. Same isolated-fragment codes,noises,weights,times,decoder and148velocity evaluations per sample. Only update cadence differs.16saved baseline controls independently audited.

| History refresh | Motif dRMS A | Motif <=1A | Coarse valid | Joint |
|---|---:|---:|---:|---:|
| outer_only | 0.417 | 1.000 | 0.406 | 0.406 |
| each_evaluation | 0.428 | 1.000 | 0.375 | 0.375 |
- Each evaluation minus outer-only motif_drms: +0.0119,95%family interval [-0.011845003458438442, 0.03806017271708696].
- Each evaluation minus outer-only coarse_valid: -0.0312,95%family interval [-0.140625, 0.09375].
- Each evaluation minus outer-only motif_success: +0.0000,95%family interval [0.0, 0.0].
- Each evaluation minus outer-only joint_success: -0.0312,95%family interval [-0.140625, 0.09375].

Qualified for fixed-sequence design/refolding: False. Generation 31.73s,peak reserved3.81GiB.

No designability, independent-test or experimental claim; all failures retained. No model parameters trained.
