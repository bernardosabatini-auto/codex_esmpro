# Isolated-fragment motif scaffolding

Status: complete.

All16fixed families/four seeds retained. Same original50/AE3/RePaint3 recipe and noise streams. Isolated fragments supply their own frame and encoder input.

| Codes | Motif dRMS A | Motif <=1A | Coarse valid | Joint |
|---|---:|---:|---:|---:|
| full_context | 0.390 | 1.000 | 0.672 | 0.672 |
| isolated | 0.417 | 1.000 | 0.406 | 0.406 |
- Isolated minus full-context motif_drms: +0.0270,95%family interval [-0.029627673950744792, 0.08548657820792868].
- Isolated minus full-context coarse_valid: -0.2656,95%family interval [-0.421875, -0.125].
- Isolated minus full-context motif_success: +0.0000,95%family interval [0.0, 0.0].
- Isolated minus full-context joint_success: -0.2656,95%family interval [-0.421875, -0.125].

Standalone fragment roundtrip mean dRMS 0.124A. Generation 31.80s, peak reserved 3.83GiB.

This practical comparison changes scaffold context, canonical frame and encoder positions; it does not isolate their causal contributions. Geometry and motif retention do not establish designability. No test structures used.
