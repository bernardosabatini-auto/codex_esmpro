# Teacher label generation

Status: complete.

512-family teacher-label pilot; this shard has 128 targets,16 samples each. AFDB references and ESMFold2 predictions, not measured equilibrium populations. All samples retained, coarse-valid mask and native-free 2A RMSD clusters supplied.

Targets: 128. Teacher samples: 2048; coarse-valid: 2041. Mean reconstruction RMSD: reference 0.1896 A, teacher sample zero 0.1744 A.

Teacher cluster-count histogram: {16: 58, 5: 4, 2: 7, 15: 9, 8: 1, 11: 2, 9: 3, 1: 23, 4: 5, 6: 1, 3: 3, 10: 2, 7: 3, 13: 5, 14: 1, 12: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Fresh reference and teacher latents use the same encoder path.
