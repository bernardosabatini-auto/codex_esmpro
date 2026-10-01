# Teacher label generation

Status: complete.

Same frozen teacher conformations, explicit reference-aligned rigid poses (frame in config); no new sampling or rejection. Training labels only.

Targets: 128. Teacher samples: 2048; coarse-valid: 2040. Mean reconstruction RMSD: reference 0.2358 A, teacher sample zero 0.1872 A.

Teacher cluster-count histogram: {16: 66, 7: 4, 6: 2, 3: 8, 15: 2, 13: 2, 1: 22, 14: 5, 12: 2, 8: 1, 9: 3, 2: 8, 4: 2, 11: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Reference latents are copied bit-for-bit from the inherited cache. Teacher latents are freshly encoded after alignment to the cached reference frame; fresh reference re-encoding is a parity check only.
