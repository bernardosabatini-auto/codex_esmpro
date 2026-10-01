# Teacher label generation

Status: complete.

512-family teacher-label pilot; this shard has 128 targets,16 samples each. AFDB references and ESMFold2 predictions, not measured equilibrium populations. All samples retained, coarse-valid mask and native-free 2A RMSD clusters supplied.

Targets: 128. Teacher samples: 2048; coarse-valid: 2041. Mean reconstruction RMSD: reference 0.3861 A, teacher sample zero 0.2060 A.

Teacher cluster-count histogram: {16: 57, 5: 7, 14: 6, 1: 20, 15: 4, 6: 6, 10: 2, 13: 6, 3: 4, 12: 3, 4: 5, 9: 1, 2: 5, 8: 2}.

Clusters are geometry-based training strata, not experimentally established states or populations. Fresh reference and teacher latents use the same encoder path.
