# Unconditional and motif generation pilot

Status: complete. Geometry is not designability. All failures retained; no generation retries.

| Head | Mode | N | Coarse valid | Motif dRMS A | Motif <=1A | Generation s | Peak GiB |
|---|---|---:|---:|---:|---:|---:|---:|
| original50 | unconditional | 64 | 1.0000 | 7.328 | 0.0000 | 11.06 | 3.83 |
| pairfree50 | unconditional | 64 | 1.0000 | 7.377 | 0.0000 | 10.78 | 3.84 |

FP32 generation only; unconditional path does not require ESM embeddings. Timings exclude loading, encoding reference motifs, numerical controls and disk I/O. Motif codes are extracted from complete reference structures and may encode scaffold context. Experimental positive controls and ProteinMPNN/refolding are still required. No same-sequence multistability, novelty, designability or general speed claim.
