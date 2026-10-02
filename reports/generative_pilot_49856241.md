# Unconditional and motif generation pilot

Status: complete. Geometry is not designability. All failures retained; no generation retries.

| Head | Mode | N | Coarse valid | Motif dRMS A | Motif <=1A | Generation s | Peak GiB |
|---|---|---:|---:|---:|---:|---:|---:|
| original10 | unconditional | 64 | 0.2969 | 7.060 | 0.0000 | 2.70 | 3.83 |
| original10 | motif_u1 | 64 | 0.0625 | 1.059 | 0.3750 | 2.69 | 3.83 |
| original10 | motif_u3 | 64 | 0.2031 | 1.002 | 0.5625 | 6.58 | 3.83 |
| reflow50 | unconditional | 64 | 0.9844 | 7.614 | 0.0000 | 10.92 | 3.85 |
| reflow50 | motif_u1 | 64 | 0.0781 | 0.610 | 0.9219 | 10.92 | 3.85 |
| reflow50 | motif_u3 | 64 | 0.5156 | 0.451 | 0.9688 | 31.76 | 3.85 |

FP32 generation only; unconditional path does not require ESM embeddings. Timings exclude loading, encoding reference motifs, numerical controls and disk I/O. Motif codes are extracted from complete reference structures and may encode scaffold context. Experimental positive controls and ProteinMPNN/refolding are still required. No same-sequence multistability, novelty, designability or general speed claim.
