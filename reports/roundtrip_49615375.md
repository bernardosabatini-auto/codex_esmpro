# ProteinAE round-trip calibration

Status: complete.

16 mapped training structures, eight paired decoder seeds, strict FP32. This validates reconstruction and decoder variability; it does not measure experimental ensemble coverage. CA coordinates and distances are in Angstrom.

| Latent / decoder steps | Mean CA RMSD | Mean CA lDDT | Mean pairwise RMSD | Peptide outlier fraction |
|---|---:|---:|---:|---:|
| fresh_steps3 | 0.1781 | 0.9994 | 0.1964 | 0.0025 |
| fresh_steps10 | 0.1778 | 0.9993 | 0.2364 | 0.0010 |
| cached_steps3 | 0.2399 | 0.9985 | 0.1997 | 0.0040 |
| cached_steps10 | 0.2184 | 0.9991 | 0.2397 | 0.0018 |

Independent-test targets were not used. Seed dispersion alone is not evidence of useful conformational diversity.
