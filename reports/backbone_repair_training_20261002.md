# Bounded backbone repair: training feasibility

Fixed122 training targets ×32 samples at two balanced2000 seeds. No reference structures in repair. All initially valid predictions remain unchanged; failed repairs return the original. No sample deletion or resampling. Coarse validity is not a physical certificate.

| Source | Invalid | Repaired | Fraction | Mean seconds/32 | Maximum seconds/32 | Feasible |
|---|---:|---:|---:|---:|---:|---|
| runs/overfit_49753133/evaluation_2000.h5 | 14 | 1 | 0.0714 | 0.0864 | 0.6547 | False |
| runs/overfit_49753251/evaluation_2000.h5 | 11 | 0 | 0.0000 | 0.0908 | 0.9085 | False |

Both-seed feasibility: **False**. Frozen requirement: at least50% of invalid samples repaired in each seed, mean added CPU time≤0.25s and maximum≤2s per32 samples, no invariant violations. Timing includes screening all samples and repair attempts, excludes cached H5 reading, startup, and independent checks.

Protocol `configs/backbone_repair_protocol.json`, SHA256 `3e7169c8c82fc844c19bfe514e57e8a6304abc5438d655948e241aa9669a803d`. Code commit `62414a48ed714266c4e5abfae79945ad008cf1fb`. Adam is coordinatewise and this prototype does not claim arbitrary-rotation equivariance; coordinate inputs retain the existing canonical frame. No native or external qualification is inferred.
