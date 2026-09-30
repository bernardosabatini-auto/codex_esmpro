# Canonical-frame stability on verified training structures

1024 training proteins; exact inherited PCA/skewness implementation. No head training or GPU use.

Largest frame difference after a proper rigid rotation and translation: 0.000370 Å.

| Input RMS perturbation | Proteins with any frame jump >1 Å | Fraction |
|---:|---:|---:|
| 0.01 Å | 0 | 0.0000 |
| 0.05 Å | 4 | 0.0039 |

This tests coordinate-frame discontinuities. It does not measure their effect on encoded latents or establish that they limit prediction accuracy.
