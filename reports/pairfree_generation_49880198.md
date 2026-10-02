# Corrected pair-free unconditional generation

Same16development families/four noises,FP32/Euler50/AE3. All128outputs audited and64original samples matched to the historical archive. No designability or inference-pipeline speed claim.

| Head | Valid /64 | Generation seconds | Peak reserved GiB |
|---|---:|---:|---:|
| original50 | 64/64 | 11.06 | 3.83 |
| pairfree50 | 64/64 | 10.78 | 3.84 |

Pair-free minus original validity: +0.00000,95%family interval [0.0, 0.0].

Generation-only original/pair-free time ratio: 1.026. One pass per head, not a repeated matched latency benchmark. Excludes loading, reference encoding, controls and writes. Unconditional sampling already skips sequence-conditioned pair computation.

The zero-width paired validity interval reflects zero observed failures in both small panels; it is not proof of population equivalence. Corrected r4b checkpoint, not either earlier confounded pair-free run. These are separately trained models; noise is paired, training seeds are not. Geometry alone cannot qualify useful proteins; a matched ProteinMPNN/refolding assay would remain required.
