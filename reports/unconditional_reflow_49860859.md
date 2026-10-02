# Unconditional trajectory compression

Status: complete.

Arm independent, profile=False, updates=1000. Training 256.55s, peak 19.69GiB, projected1000updates including evaluation/startup 311.2s. Profile qualified: False.

| Step | Raw coarse validity | CA-lDDT to same-noise original50 | Geometry screen |
|---|---:|---:|---|
| 0 | 0.2969 | 0.5177 | False |
| 500 | 0.1875 | 0.4918 | False |
| 1000 | 0.1406 | 0.4854 | False |

Raw unconditional output; mapping fidelity is descriptive, not a generative accuracy gate. No designability or conditional-folding qualification.

All64 outputs retained at every endpoint; unchanged original10 initial outputs, learned-null/generic CFG0 controls and frozen unused weights verified. Training labels contain no sequence inputs. Locked tests remain unscored.
