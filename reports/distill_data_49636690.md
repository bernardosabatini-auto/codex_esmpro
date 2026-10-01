# Teacher label generation

Status: complete.

512-family teacher-label pilot; this shard has 128 targets,16 samples each. AFDB references and ESMFold2 predictions, not measured equilibrium populations. All samples retained, coarse-valid mask and native-free 2A RMSD clusters supplied.

Targets: 128. Teacher samples: 2048; coarse-valid: 2035. Mean reconstruction RMSD: reference 0.1780 A, teacher sample zero 0.1836 A.

Teacher cluster-count histogram: {16: 57, 6: 2, 2: 10, 10: 3, 15: 12, 14: 3, 3: 4, 1: 21, 13: 2, 4: 3, 12: 1, 7: 5, 5: 1, 8: 1, 9: 2, 11: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Fresh reference and teacher latents use the same encoder path.
