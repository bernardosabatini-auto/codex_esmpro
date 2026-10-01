# Teacher label generation

Status: complete.

512-family teacher-label pilot; this shard has 128 targets,16 samples each. AFDB references and ESMFold2 predictions, not measured equilibrium populations. All samples retained, coarse-valid mask and native-free 2A RMSD clusters supplied.

Targets: 128. Teacher samples: 2048; coarse-valid: 2040. Mean reconstruction RMSD: reference 0.2326 A, teacher sample zero 0.1772 A.

Teacher cluster-count histogram: {16: 66, 7: 4, 6: 2, 3: 8, 15: 2, 13: 2, 1: 22, 14: 5, 12: 2, 8: 1, 9: 3, 2: 8, 4: 2, 11: 1}.

Clusters are geometry-based training strata, not experimentally established states or populations. Fresh reference and teacher latents use the same encoder path.
