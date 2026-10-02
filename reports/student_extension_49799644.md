# Student128-sample extension

Status: complete; pipeline: compact500.

All16 frozen two-state development families. Original first32 coverage prefixes must match at1/2/3A. All samples retained; fixed decoder noise and varied latent noise. This diagnoses observed state reachability, not thermodynamic populations or model promotion.

| K | Mean coverage | Families hitting both states | Valid fraction | Oracle CA-lDDT |
|---|---:|---:|---:|---:|
| 1 | 0.18750 | 0/16 | 1.00000 | 0.89950 |
| 4 | 0.31250 | 0/16 | 1.00000 | 0.90341 |
| 16 | 0.43750 | 1/16 | 0.98828 | 0.90194 |
| 32 | 0.43750 | 1/16 | 0.99023 | 0.90231 |
| 64 | 0.43750 | 1/16 | 0.99219 | 0.90111 |
| 128 | 0.43750 | 1/16 | 0.99365 | 0.90155 |

128 minus32 coverage: +0.00000,95% paired-family interval[0.0, 0.0].

128 minus32 both_states: +0.00000,95% paired-family interval[0.0, 0.0].

128 minus32 valid_fraction: +0.00342,95% paired-family interval[-0.00439453125, 0.0146484375].

128 minus32 oracle_ca_lddt: -0.00076,95% paired-family interval[-0.0023678848724790593, 0.000625038223319665].

Student128 minus teacher128 coverage: -0.28125,95% paired-family interval[-0.46875, -0.125].

Student128 minus teacher128 both_states: -0.37500,95% paired-family interval[-0.625, -0.125].

Cached-conditioner generation316.32s for16×128 samples; peak reserved45.93GiB. Excludes ESMC, loading, prefix controls and disk I/O; no end-to-end speed claim.
