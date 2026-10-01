# Teacher label generation

Status: complete.

Same frozen teacher conformations, explicit reference-aligned rigid poses (frame in config); no new sampling or rejection. Training labels only.

Targets: 128. Teacher samples: 2048; coarse-valid: 2041. Mean reconstruction RMSD: reference 0.2303 A, teacher sample zero 0.1963 A.

Teacher cluster-count histogram: {16: 58, 5: 4, 2: 7, 15: 9, 8: 1, 11: 2, 9: 3, 1: 23, 4: 5, 6: 1, 3: 3, 10: 2, 7: 3, 13: 5, 14: 1, 12: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Reference latents are copied bit-for-bit from the inherited cache. Teacher latents are freshly encoded after alignment to the cached reference frame; fresh reference re-encoding is a parity check only.
