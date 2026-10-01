# Teacher label generation

Status: complete.

Same frozen teacher conformations, explicit reference-aligned rigid poses (frame in config); no new sampling or rejection. Training labels only.

Targets: 128. Teacher samples: 2048; coarse-valid: 2035. Mean reconstruction RMSD: reference 0.1871 A, teacher sample zero 0.1888 A.

Teacher cluster-count histogram: {16: 57, 6: 2, 2: 10, 10: 3, 15: 12, 14: 3, 3: 4, 1: 21, 13: 2, 4: 3, 12: 1, 7: 5, 5: 1, 8: 1, 9: 2, 11: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Reference latents are copied bit-for-bit from the inherited cache. Teacher latents are freshly encoded after alignment to the cached reference frame; fresh reference re-encoding is a parity check only.
