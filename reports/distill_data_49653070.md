# Teacher label generation

Status: complete.

Same frozen teacher conformations, explicit reference-aligned rigid poses (frame in config); no new sampling or rejection. Training labels only.

Targets: 128. Teacher samples: 2048; coarse-valid: 2041. Mean reconstruction RMSD: reference 0.4635 A, teacher sample zero 0.2248 A.

Teacher cluster-count histogram: {16: 57, 5: 7, 14: 6, 1: 20, 15: 4, 6: 6, 10: 2, 13: 6, 3: 4, 12: 3, 4: 5, 9: 1, 2: 5, 8: 2}.

Clusters are geometry-based training strata, not experimentally established states or populations. Reference latents are copied bit-for-bit from the inherited cache. Teacher latents are freshly encoded after alignment to the cached reference frame; fresh reference re-encoding is a parity check only.
