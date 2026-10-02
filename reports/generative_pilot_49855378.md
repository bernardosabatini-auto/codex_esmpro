# Unconditional and motif generation pilot

Status: complete. Geometry is not designability. All failures retained; no generation retries.

| Head | Mode | N | Coarse valid | Motif dRMS A | Motif <=1A | Generation s | Peak GiB |
|---|---|---:|---:|---:|---:|---:|---:|
| original50 | unconditional | 64 | 1.0000 | 7.328 | 0.0000 | 10.96 | 3.83 |
| original50 | motif_u1 | 64 | 0.1094 | 0.591 | 0.9375 | 10.94 | 3.83 |
| original50 | motif_u3 | 64 | 0.6719 | 0.390 | 1.0000 | 31.82 | 3.83 |
| reflow10 | unconditional | 64 | 0.7188 | 7.142 | 0.0000 | 2.64 | 3.85 |
| reflow10 | motif_u1 | 64 | 0.0938 | 1.227 | 0.2188 | 2.64 | 3.85 |
| reflow10 | motif_u3 | 64 | 0.2344 | 1.103 | 0.5000 | 6.45 | 3.85 |

FP32 generation only; unconditional path does not require ESM embeddings. Timings exclude loading, encoding reference motifs, numerical controls and disk I/O. Motif codes are extracted from complete reference structures and may encode scaffold context. Experimental positive controls and ProteinMPNN/refolding are still required. No same-sequence multistability, novelty, designability or general speed claim.
