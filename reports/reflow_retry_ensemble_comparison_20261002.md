# Archived10-step bounded-retry external comparison

All48 development families,16 state-eligible families, unchanged thresholds and all failures retained. Frozen original and compact25-step controls reused through exact native/source lineage. New10-step candidate uses expanded conditioning; compact500 uses compact conditioning.

| Reference | Selected metric | Reflow10 | Reference | Difference |95% family interval |
|---|---|---:|---:|---:|---|
| original | coverage_at_32 | 0.43750 | 0.43750 | +0.00000 | [-0.09375, 0.09375] |
| original | both_states | 0.06250 | 0.06250 | +0.00000 | [0.0, 0.0] |
| original | ca_lddt | 0.87184 | 0.86796 | +0.00388 | [0.00017645776227858358, 0.007212775833754569] |
| original | coarse_valid | 1.00000 | 1.00000 | +0.00000 | [0.0, 0.0] |
| original | md_w1 | 0.48305 | 0.48850 | -0.00545 | [-0.013427120949362126, 0.0009121982700599372] |
| compact500 | coverage_at_32 | 0.43750 | 0.43750 | +0.00000 | [0.0, 0.0] |
| compact500 | both_states | 0.06250 | 0.06250 | +0.00000 | [0.0, 0.0] |
| compact500 | ca_lddt | 0.87184 | 0.87286 | -0.00102 | [-0.00342218910907703, 0.001259510695753653] |
| compact500 | coarse_valid | 1.00000 | 1.00000 | +0.00000 | [0.0, 0.0] |
| compact500 | md_w1 | 0.48305 | 0.48941 | -0.00636 | [-0.015047383256564325, 0.0007447929683568477] |

External quality versus original:True; versus compact500:True.

original: recovered9/9, exhausted0; attempts/output1.00716; generation264.77s + retries5.34s; peak41.93GiB.

compact500: recovered6/6, exhausted0; attempts/output1.00391; generation131.47s + retries1.87s; peak41.89GiB.

reflow10: recovered6/6, exhausted0; attempts/output1.00456; generation66.14s + retries1.35s; peak41.91GiB.

MD W1 is better when lower and always reported. Cached-conditioner generation timings exclude ESM, geometry checks, loading and I/O: no end-to-end speed claim. Passing original does not imply equivalence to compact. Raw native failure remains unchanged. No equilibrium, independent-test or new-diversity claim; locked tests unscored.
