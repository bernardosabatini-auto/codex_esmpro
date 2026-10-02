# Unconditional trajectory compression

Status: complete.

Arm paired, profile=False, updates=1000. Training 256.65s, peak 19.69GiB, projected1000updates including evaluation/startup 324.1s. Profile qualified: False.

| Step | Raw coarse validity | CA-lDDT to same-noise original50 | Geometry screen |
|---|---:|---:|---|
| 0 | 0.2969 | 0.5177 | False |
| 500 | 0.9375 | 0.4630 | False |
| 1000 | 0.8906 | 0.4810 | False |

Raw unconditional output; mapping fidelity is descriptive, not a generative accuracy gate. No designability or conditional-folding qualification.

All64 outputs retained at every endpoint; unchanged original10 initial outputs, learned-null/generic CFG0 controls and frozen unused weights verified. Training labels contain no sequence inputs. Locked tests remain unscored.
