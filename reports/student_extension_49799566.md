# Student128-sample extension

Status: complete; pipeline: original.

All16 frozen two-state development families. Original first32 coverage prefixes must match at1/2/3A. All samples retained; fixed decoder noise and varied latent noise. This diagnoses observed state reachability, not thermodynamic populations or model promotion.

| K | Mean coverage | Families hitting both states | Valid fraction | Oracle CA-lDDT |
|---|---:|---:|---:|---:|
| 1 | 0.28125 | 0/16 | 1.00000 | 0.89020 |
| 4 | 0.34375 | 0/16 | 1.00000 | 0.89439 |
| 16 | 0.43750 | 1/16 | 0.98438 | 0.89396 |
| 32 | 0.43750 | 1/16 | 0.98242 | 0.89329 |
| 64 | 0.46875 | 1/16 | 0.98242 | 0.89286 |
| 128 | 0.46875 | 1/16 | 0.97852 | 0.89261 |

128 minus32 coverage: +0.03125,95% paired-family interval[0.0, 0.09375].

128 minus32 both_states: +0.00000,95% paired-family interval[0.0, 0.0].

128 minus32 valid_fraction: -0.00391,95% paired-family interval[-0.0107421875, 0.0009765625].

128 minus32 oracle_ca_lddt: -0.00068,95% paired-family interval[-0.0012680090856444942, -9.657754910062751e-06].

Student128 minus teacher128 coverage: -0.25000,95% paired-family interval[-0.40625, -0.09375].

Student128 minus teacher128 both_states: -0.37500,95% paired-family interval[-0.625, -0.125].

Cached-conditioner generation644.84s for16×128 samples; peak reserved45.93GiB. Excludes ESMC, loading, prefix controls and disk I/O; no end-to-end speed claim.
