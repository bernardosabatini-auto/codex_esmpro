# Unconditional trajectory compression

Status: complete.

Arm paired, profile=True, updates=40. Training 11.48s, peak 19.68GiB, projected1000updates including evaluation/startup 384.1s. Profile qualified: True.

| Step | Raw coarse validity | CA-lDDT to same-noise original50 | Geometry screen |
|---|---:|---:|---|
| 0 | 0.2969 | 0.5177 | False |
| 40 | 0.3125 | 0.5154 | False |

Raw unconditional output; mapping fidelity is descriptive, not a generative accuracy gate. No designability or conditional-folding qualification.

All64 outputs retained at every endpoint; unchanged original10 initial outputs, learned-null/generic CFG0 controls and frozen unused weights verified. Training labels contain no sequence inputs. Locked tests remain unscored.
